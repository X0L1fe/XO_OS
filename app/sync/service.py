from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy.orm import Session

from app.database.models import UserStats, Lesson, ScheduleExclusion
from app.google_calendar.service import GoogleCalendarService
from app.ics.parser import parse_ics_data
from app.schemas import SyncResult
from app.sync.diff import calculate_diff


class SyncService:
    def __init__(self, db_session: Session, google_calendar_service: Optional[GoogleCalendarService] = None):
        self.db = db_session
        self.google_calendar_service = google_calendar_service

    def sync_multiple_calendars(
        self, ics_data_list: List[str], *, user_id: int
    ) -> SyncResult:
        """
        Sync multiple iCal data strings for a user.
        """
        # Parse all iCal data
        all_parsed = []
        for ics_data in ics_data_list:
            parsed = parse_ics_data(ics_data)
            all_parsed.extend(parsed)

        # Calculate diff between existing lessons and parsed lessons
        diff = self._calculate_diff(existing_lessons=self._get_existing_lessons(user_id), parsed_lessons=all_parsed)

        # Apply changes: create, update, delete lessons
        self._apply_changes(diff, user_id=user_id)

        # Update statistics and gamification
        # NOTE: We have removed the XP and streak logic from here as per the new requirements.
        # Synchronization does not award XP or streak.
        # self._update_stats(
        #     len(diff.created),
        #     user_id=user_id,
        # )

        return SyncResult(
            parsed=len(all_parsed),
            created=len(diff.created),
            updated=len(diff.updated),
            moved=len(diff.moved),
            deleted=len(diff.deleted),
        )

    def _get_existing_lessons(self, user_id: int) -> List[Lesson]:
        """
        Get existing lessons for a user.
        """
        return (
            self.db.query(Lesson)
            .filter(Lesson.user_id == user_id)
            .order_by(Lesson.start_time)
            .all()
        )

    def _calculate_diff(self, existing_lessons: List[Lesson], parsed_lessons: List[dict]) -> dict:
        """
        Calculate the difference between existing lessons and parsed lessons.
        Returns a dict with keys: created, updated, moved, deleted.
        """
        return calculate_diff(existing_lessons, parsed_lessons)

    def _apply_changes(self, diff: dict, *, user_id: int) -> None:
        """
        Apply the changes to the database.
        """
        # Create new lessons
        for lesson_data in diff.get("created", []):
            lesson = Lesson(
                user_id=user_id,
                **lesson_data,
            )
            self.db.add(lesson)

        # Update existing lessons
        for lesson_data in diff.get("updated", []):
            lesson_id = lesson_data.pop("id")
            lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                for key, value in lesson_data.items():
                    setattr(lesson, key, value)

        # Move lessons (update time and possibly other fields)
        for lesson_data in diff.get("moved", []):
            lesson_id = lesson_data.pop("id")
            lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                for key, value in lesson_data.items():
                    setattr(lesson, key, value)

        # Delete lessons
        for lesson_id in diff.get("deleted", []):
            lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
            if lesson:
                self.db.delete(lesson)

        self.db.commit()

    # NOTE: The _update_stats method has been removed because synchronization should not award XP or streak.
    # We keep the method here as a placeholder in case we need it for something else, but it does nothing.
    def _update_stats(
        self,
        lessons_imported: int,
        *,
        user_id: int,
    ) -> None:
        """
        This method is intentionally left empty because synchronization does not award XP or streak.
        XP and streak are only awarded through focus sessions.
        """
        pass