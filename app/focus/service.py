from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.database.models import (
    FocusEvidence,
    FocusSession,
    Lesson,
    ScheduleExclusion,
    User,
    UserStats,
    XPTransaction,
)

# Import event publishing functions
from app.event import publish_focus_updated, publish_gamification_updated


def normalize_schedule_category(category: str) -> str:
    """Normalize schedule category for comparison."""
    if not category or category.strip() == "":
        return "OTHER"
    return category.strip().upper()


def lesson_is_visible(
    lesson: Lesson, excluded_categories: set, excluded_subjects: set
) -> bool:
    """Check if a lesson should be visible based on user's exclusions."""
    if lesson_is_excluded_by_category(lesson, excluded_categories):
        return False
    if lesson_is_excluded_by_subject(lesson, excluded_subjects):
        return False
    return True


def lesson_is_excluded_by_category(lesson: Lesson, excluded_categories: set) -> bool:
    """Check if lesson is excluded by category."""
    lesson_category = normalize_schedule_category(lesson.category or "")
    return lesson_category in excluded_categories


def lesson_is_excluded_by_subject(lesson: Lesson, excluded_subjects: set) -> bool:
    """Check if lesson is excluded by subject."""
    lesson_subject = (lesson.subject or "").strip().lower()
    return lesson_subject in excluded_subjects


class FocusService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def start_focus_session(
        self, user_id: int, goal_text: Optional[str] = None
    ) -> FocusSession:
        """
        Start a new focus session for the user.
        The backend determines the current lesson based on time and user's schedule exclusions.
        If there is already an active session, return it.
        """
        # Check for existing active session
        active_session = (
            self.db.query(FocusSession)
            .filter(FocusSession.user_id == user_id, FocusSession.status == "active")
            .first()
        )
        if active_session:
            return active_session

        # Determine the current lesson based on time and schedule exclusions
        current_lesson = self.get_current_lesson(user_id)

        # Create new focus session
        new_session = FocusSession(
            user_id=user_id,
            lesson_id=current_lesson.id if current_lesson else None,
            goal_text=goal_text,
            status="active",
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return new_session

    def pause_focus_session(self, session_id: int, user_id: int) -> FocusSession:
        """
        Pause an active focus session.
        """
        session = (
            self.db.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
                FocusSession.status == "active",
            )
            .first()
        )
        if not session:
            raise ValueError("Active focus session not found")

        if session.paused_at is not None:
            # Already paused
            return session

        session.paused_at = datetime.now(timezone.utc)
        session.status = "paused"
        self.db.commit()
        self.db.refresh(session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return session

    def resume_focus_session(self, session_id: int, user_id: int) -> FocusSession:
        """
        Resume a paused focus session.
        """
        session = (
            self.db.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
                FocusSession.status == "paused",
            )
            .first()
        )
        if not session:
            raise ValueError("Paused focus session not found")

        if session.paused_at is None:
            # Not paused
            return session

        # Calculate the paused duration and add to total_paused_seconds
        now = datetime.now(timezone.utc)
        paused_duration = (now - session.paused_at).total_seconds()
        session.total_paused_seconds += int(paused_duration)
        session.paused_at = None
        session.status = "active"
        self.db.commit()
        self.db.refresh(session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return session

    def complete_focus_session(
        self,
        session_id: int,
        user_id: int,
        completion_mode: str = "manual",
        evidence: Optional[List[dict]] = None,
    ) -> FocusSession:
        """
        Complete a focus session.
        If completion_mode is "manual", we award base XP and set verification_status to "not_required".
        If completion_mode is "ai_verified", we start the AI verification process (asynchronous) and set verification_status to "pending".
        The actual XP awarding for AI verification will happen after the verification completes.
        """
        session = (
            self.db.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
                FocusSession.status.in_(["active", "paused"]),
            )
            .first()
        )
        if not session:
            raise ValueError("Focus session not found or not in a completable state")

        # Check if we have already rewarded XP for this lesson occurrence
        # This prevents farming XP by creating multiple focus sessions for the same lesson
        if session.lesson_id:
            existing_rewarded_session = (
                self.db.query(FocusSession)
                .filter(
                    FocusSession.user_id == user_id,
                    FocusSession.lesson_id == session.lesson_id,
                    FocusSession.status == "completed",
                    FocusSession.xp_awarded > 0,
                    FocusSession.id != session_id,  # Exclude current session
                )
                .first()
            )
            if existing_rewarded_session:
                raise ValueError(
                    "XP has already been awarded for this lesson occurrence"
                )

        # Set ended_at and calculate duration
        now = datetime.now(timezone.utc)
        session.ended_at = now

        # Calculate total duration and productive duration (excluding pauses)
        total_duration = (session.ended_at - session.started_at).total_seconds()
        productive_duration = total_duration - session.total_paused_seconds
        session.duration_seconds = int(total_duration)

        # If the session was paused, we need to adjust the ended_at? Actually, we set ended_at to now, and productive_duration is total_duration minus paused time.
        # We'll store the productive duration separately if needed, but for now we only store total duration.

        # Save evidence if provided
        if evidence:
            for ev in evidence:
                new_evidence = FocusEvidence(
                    focus_session_id=session.id,
                    type=ev["type"],
                    content=ev.get("content", ""),
                    file_path=ev.get("file_path"),
                )
                self.db.add(new_evidence)
            session.evidence_provided = True

        session.completion_mode = completion_mode
        session.status = "completed"

        if completion_mode == "manual":
            # Manual completion: award base XP (e.g., 3 XP)
            base_xp = 3
            session.xp_awarded = base_xp
            session.verification_status = "not_required"
            # Award the XP immediately
            self._award_xp(user_id, base_xp, "focus_completed", session.id)
        elif completion_mode == "ai_verified":
            # AI verified: we don't award XP yet, we set verification_status to pending and will award after verification
            session.verification_status = "pending"
            # We do not commit the session yet because we want to wait for the AI verification result?
            # Actually, we can commit the session with pending status and then update it after verification.
            # But note: the user wants the completion to be asynchronous, so we return the session in pending state.
            # We'll commit the session now with pending status, and then the AI verification will update it later.
            self.db.commit()
            self.db.refresh(session)
            # Publish focus updated event
            publish_focus_updated(user_id)
            # TODO: Trigger AI verification in the background (e.g., using a background task or a separate process)
            # For now, we'll just return the session and the caller (the API) can trigger the verification.
            # We'll leave the actual verification to the API layer.
            return session
        else:
            raise ValueError("Invalid completion mode")

        # For manual completion, we commit the session and award XP
        self.db.commit()
        self.db.refresh(session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return session

    def _award_xp(
        self, user_id: int, amount: int, reason: str, source_id: Optional[int] = None
    ) -> None:
        """
        Award XP to the user and update UserStats.
        This is called when XP is to be awarded (e.g., after manual completion or after AI verification approval).
        """
        # Create XP transaction
        xp_transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            reason=reason,
            source_type="focus_session",
            source_id=source_id,
        )
        self.db.add(xp_transaction)

        # Update UserStats
        stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)

        stats.total_xp += amount
        # Update level: every 1000 XP = 1 level
        new_level = (stats.total_xp // 1000) + 1
        if new_level > stats.level:
            stats.level = new_level

        # Update streak: we consider today's date for streak
        today = datetime.now(timezone.utc).date()
        if stats.last_activity_date:
            last_activity_date = stats.last_activity_date.date()
            if today == last_activity_date:
                # Same day, streak remains the same (we only increment once per day)
                pass
            elif today == last_activity_date + timedelta(days=1):
                # Consecutive day
                stats.current_streak += 1
            else:
                # Gap in days, reset streak
                stats.current_streak = 1
        else:
            # First activity
            stats.current_streak = 1

        # Update max streak if needed
        if stats.current_streak > stats.max_streak:
            stats.max_streak = stats.current_streak

        stats.last_activity_date = datetime.now(timezone.utc)
        self.db.commit()

        # Publish gamification updated event
        publish_gamification_updated(user_id)

    def get_active_session(self, user_id: int) -> Optional[FocusSession]:
        """
        Get the active focus session for the user, if any.
        """
        return (
            self.db.query(FocusSession)
            .filter(FocusSession.user_id == user_id, FocusSession.status == "active")
            .first()
        )

    def get_session(self, session_id: int, user_id: int) -> Optional[FocusSession]:
        """
        Get a focus session by ID, ensuring it belongs to the user.
        """
        return (
            self.db.query(FocusSession)
            .filter(FocusSession.id == session_id, FocusSession.user_id == user_id)
            .first()
        )

    def get_current_lesson(self, user_id: int) -> Optional[Lesson]:
        """
        Get the current visible lesson for a user based on current time and schedule exclusions.
        Backend determines the current lesson - does not trust frontend input.
        """
        now = datetime.now(timezone.utc)

        # Get user's schedule exclusions
        excluded_categories, excluded_subjects = self._get_schedule_exclusions(user_id)

        # Find lessons that are currently happening
        lessons = (
            self.db.query(Lesson)
            .filter(
                Lesson.user_id == user_id,
                Lesson.start_time <= now,
                Lesson.end_time >= now,
            )
            .order_by(Lesson.start_time)
            .all()
        )

        # Return the first visible lesson
        lesson = next(
            (
                item
                for item in lessons
                if lesson_is_visible(
                    item,
                    excluded_categories,
                    excluded_subjects,
                )
            ),
            None,
        )
        return lesson

    def _get_schedule_exclusions(self, user_id: int) -> tuple[set, set]:
        """
        Get the user's schedule exclusions as sets of normalized category and subject values.
        Returns (excluded_categories, excluded_subjects).
        """
        exclusions = (
            self.db.query(ScheduleExclusion)
            .filter(ScheduleExclusion.user_id == user_id)
            .all()
        )

        excluded_categories = set()
        excluded_subjects = set()

        for exclusion in exclusions:
            if exclusion.exclusion_type == "category":
                excluded_categories.add(
                    normalize_schedule_category(exclusion.value_key)
                )
            elif exclusion.exclusion_type == "subject":
                excluded_subjects.add(exclusion.value_key.lower().strip())

        return excluded_categories, excluded_subjects

    def add_evidence(
        self, session_id: int, user_id: int, evidence: dict
    ) -> FocusEvidence:
        """
        Add evidence to a focus session.
        """
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Focus session not found")
        if session.status not in ["active", "paused"]:
            raise ValueError(
                "Cannot add evidence to a session that is not active or paused"
            )

        new_evidence = FocusEvidence(
            focus_session_id=session.id,
            type=evidence["type"],
            content=evidence.get("content", ""),
            file_path=evidence.get("file_path"),
        )
        self.db.add(new_evidence)
        session.evidence_provided = True
        self.db.commit()
        self.db.refresh(new_evidence)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return new_evidence
