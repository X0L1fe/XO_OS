from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import List, Optional, Protocol

from app.common.time import utc_now
from app.database.db import Database
from app.database.models import Lesson, User, UserStats
from app.ics.parser import LessonData, parse_ics
from app.sync.diff import DiffResult, LessonChange, calculate_diff
from sqlalchemy import select


class GoogleCalendarServiceProtocol(Protocol):
    def sync_changes(self, diff: DiffResult) -> None: ...


@dataclass(frozen=True, slots=True)
class SyncResult:
    parsed: int
    created: int
    updated: int
    moved: int
    deleted: int
    unchanged: int

    diff: DiffResult

    @property
    def changes(self) -> tuple[LessonChange, ...]:
        return self.diff.changes


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _apply_lesson_data(
    lesson: Lesson,
    data: LessonData,
    *,
    now: datetime,
    mais_group_id: Optional[str] = None,
) -> None:
    """
    Обновляет существующую БД-запись данными из ICS.
    """
    lesson.stable_id = data.identity_key
    lesson.source_uid = data.source_uid

    lesson.subject = data.subject
    lesson.lesson_type = data.lesson_type
    lesson.category = data.category

    lesson.start_time = data.start_time
    lesson.end_time = data.end_time

    lesson.teacher = data.teacher
    lesson.room = data.room
    lesson.description = data.description

    lesson.content_hash = data.content_hash
    lesson.raw_ics = data.raw_ics

    lesson.last_seen_at = now
    lesson.mais_group_id = mais_group_id


def _create_lesson(
    data: LessonData,
    *,
    now: datetime,
    user_id: int,
    mais_group_id: Optional[str] = None,
) -> Lesson:
    return Lesson(
        stable_id=data.identity_key,
        source_uid=data.source_uid,
        subject=data.subject,
        lesson_type=data.lesson_type,
        category=data.category,
        start_time=data.start_time,
        end_time=data.end_time,
        teacher=data.teacher,
        room=data.room,
        description=data.description,
        content_hash=data.content_hash,
        last_synced_content_hash=None,
        raw_ics=data.raw_ics,
        first_seen_at=now,
        last_seen_at=now,
        user_id=user_id,
        mais_group_id=mais_group_id,
    )


class SyncService:
    def __init__(
        self,
        db: Database,
        google_calendar_service: Optional[GoogleCalendarServiceProtocol] = None,
    ):
        self.db = db
        self.google_calendar_service = google_calendar_service

    def import_ics(
        self,
        content: bytes,
        *,
        user_id: int,
        include_military: bool = False,
    ) -> SyncResult:
        incoming = parse_ics(
            content,
            include_military=include_military,
        )

        # Empty import must never delete existing schedule.
        if not incoming:
            empty_diff = DiffResult(
                created=(),
                updated=(),
                moved=(),
                deleted=(),
                unchanged=(),
            )

            return SyncResult(
                parsed=0,
                created=0,
                updated=0,
                moved=0,
                deleted=0,
                unchanged=0,
                diff=empty_diff,
            )

        min_date = min(lesson.start_time.date() for lesson in incoming)
        max_date = max(lesson.start_time.date() for lesson in incoming)

        incoming_map = {lesson.identity_key: lesson for lesson in incoming}

        with self.db.session() as session:
            # Get the user's MAIS group ID
            user_obj = session.query(User).filter(User.id == user_id).one()
            mais_group_id = user_obj.mais_group_id
            # IMPORTANT:
            #
            # We only look at the date range of the current ICS.
            #
            # Therefore:
            #
            # semester.ics
            #     → compares the whole semester
            #
            # week.ics
            #     → compares only this week
            #
            # and does not destroy the rest of the semester's lessons.

            range_start = datetime.combine(
                min_date,
                time.min,
            )

            range_end = datetime.combine(
                max_date,
                time.max,
            )

            existing = session.scalars(
                select(Lesson).where(
                    Lesson.user_id == user_id,
                    Lesson.start_time >= range_start,
                    Lesson.start_time <= range_end,
                )
            ).all()

            diff = calculate_diff(
                existing,
                incoming_map.values(),
            )

            now = utc_now()

            # -------------------------------------------------
            # CREATED
            # -------------------------------------------------

            for change in diff.created:
                assert change.new is not None

                session.add(
                    _create_lesson(
                        change.new,
                        now=now,
                        user_id=user_id,
                        mais_group_id=mais_group_id,
                    )
                )

            # -------------------------------------------------
            # UPDATED
            # -------------------------------------------------

            for change in diff.updated:
                assert change.old is not None
                assert change.new is not None

                _apply_lesson_data(
                    change.old,
                    change.new,
                    now=now,
                    mais_group_id=mais_group_id,
                )

            # -------------------------------------------------
            # MOVED
            # -------------------------------------------------

            for change in diff.moved:
                assert change.old is not None
                assert change.new is not None

                # Key point:
                #
                # We do NOT delete the old DB record.
                #
                # We change its content and stable_id.
                #
                # Thanks to this, calendar_events
                # will continue to reference the same lesson.id.
                _apply_lesson_data(
                    change.old,
                    change.new,
                    now=now,
                    mais_group_id=mais_group_id,
                )

            # -------------------------------------------------
            # UNCHANGED
            # -------------------------------------------------

            for change in diff.unchanged:
                assert change.old is not None

                change.old.last_seen_at = now

            # -------------------------------------------------
            # DELETED
            # -------------------------------------------------

            for change in diff.deleted:
                assert change.old is not None

                session.delete(change.old)

            session.commit()

            # Synchronize changes to Google Calendar if a service is provided.
            print("-> Вызов синхронизации Google Calendar, diff:", diff)
            if self.google_calendar_service is not None:
                self.google_calendar_service.sync_changes(diff)

        # Update statistics and gamification
        self._update_stats(
            len(incoming),
            user_id=user_id,
        )
        return SyncResult(
            parsed=len(incoming),
            created=len(diff.created),
            updated=len(diff.updated),
            moved=len(diff.moved),
            deleted=len(diff.deleted),
            unchanged=len(diff.unchanged),
            diff=diff,
        )

    def status(self, user_id: int) -> str:
        with self.db.session() as session:
            lessons = session.scalars(
                select(Lesson).where(Lesson.user_id == user_id)
            ).all()

            return f"lessons={len(lessons)}"

    def export_to_obsidian(
        self,
        vault_path: str,
        *,
        user_id: int,
    ) -> int:
        """
        Export all lessons to an Obsidian vault.
        Creates markdown files in subdirectories by lesson type.
        Returns the number of lessons exported.
        """
        # Ensure the vault path exists
        os.makedirs(vault_path, exist_ok=True)

        with self.db.session() as session:
            lessons = session.query(Lesson).filter(Lesson.user_id == user_id).all()

        exported = 0
        for lesson in lessons:
            # Determine the folder for this lesson type
            lesson_type_folder = lesson.lesson_type
            # If the lesson_type is not one of the expected, we can use 'OTHER'
            if lesson_type_folder not in [
                "LECTURE",
                "PRACTICE",
                "LAB",
                "EXAM",
                "OTHER",
            ]:
                lesson_type_folder = "OTHER"

            # Create the directory for this lesson type
            type_dir = os.path.join(vault_path, lesson_type_folder)
            os.makedirs(type_dir, exist_ok=True)

            # Create a safe filename using the stable_id (which is already a hex string, safe for filenames)
            filename = f"{lesson.stable_id}.md"
            file_path = os.path.join(type_dir, filename)

            # Prepare the markdown content
            start_time_str = lesson.start_time.strftime("%d.%m.%Y %H:%M")
            end_time_str = lesson.end_time.strftime("%H:%M")
            teacher_str = lesson.teacher or "Не указан"
            room_str = lesson.room or "Не указана"
            description_str = lesson.description or ""

            content = f"""
                # {lesson.subject}
                **Тип:** {lesson.lesson_type}
                **Категория:** {lesson.category}
                **Преподаватель:** {teacher_str}
                **Аудитория:** {room_str}
                **Описание:** {description_str}
                **Время:** {start_time_str} - {end_time_str}
                """

            # Write the file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            exported += 1

        return exported

    def _update_stats(
        self,
        lessons_imported: int,
        *,
        user_id: int,
    ) -> None:
        """
        Update user statistics and gamification data.
        Does NOT award XP for imported lessons (XP only for completed focus sessions).
        Updates streak based on daily activity.
        """
        with self.db.session() as session:
            # Get or create the stats row (singleton pattern)
            stats = (
                session.query(UserStats).filter(UserStats.user_id == user_id).first()
            )
            if not stats:
                stats = UserStats(
                    user_id=user_id,
                    level=1,
                    max_streak=0,
                )
                session.add(stats)

            # Update streak based on lesson import activity
            today = datetime.now(timezone.utc).date()
            if stats.last_activity_date:
                last_activity = stats.last_activity_date.date()
                if today == last_activity:
                    # Same day, streak continues
                    pass
                elif today == last_activity + timedelta(days=1):
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

            # Update last activity date
            stats.last_activity_date = datetime.now(timezone.utc)

            session.commit()

    def import_lesson_data(
        self,
        lesson_data: List[LessonData],
        *,
        user_id: int,
        include_military: bool = False,
        mais_group_id: Optional[str] = None,
    ) -> SyncResult:
        """
        Import a list of LessonData objects (parsed from MAIS schedule or other source).
        Similar to import_ics but skips the parsing step.
        """
        incoming = lesson_data

        # Empty import must not delete existing schedule.
        if not incoming:
            empty_diff = DiffResult(
                created=(),
                updated=(),
                moved=(),
                deleted=(),
                unchanged=(),
            )

            return SyncResult(
                parsed=0,
                created=0,
                updated=0,
                moved=0,
                deleted=0,
                unchanged=0,
                diff=empty_diff,
            )

        min_date = min(lesson.start_time.date() for lesson in incoming)
        max_date = max(lesson.start_time.date() for lesson in incoming)

        incoming_map = {lesson.identity_key: lesson for lesson in incoming}

        with self.db.session() as session:
            range_start = datetime.combine(
                min_date,
                time.min,
            )

            range_end = datetime.combine(
                max_date,
                time.max,
            )

            existing = session.scalars(
                select(Lesson).where(
                    Lesson.user_id == user_id,
                    Lesson.start_time >= range_start,
                    Lesson.start_time <= range_end,
                )
            ).all()

            diff = calculate_diff(
                existing,
                incoming_map.values(),
            )

            now = utc_now()

            # CREATED
            for change in diff.created:
                assert change.new is not None
                session.add(
                    _create_lesson(
                        change.new,
                        now=now,
                        user_id=user_id,
                        mais_group_id=mais_group_id,
                    )
                )

            # UPDATED
            for change in diff.updated:
                assert change.old is not None
                assert change.new is not None
                _apply_lesson_data(
                    change.old,
                    change.new,
                    now=now,
                    mais_group_id=mais_group_id,
                )

            # MOVED
            for change in diff.moved:
                assert change.old is not None
                assert change.new is not None
                _apply_lesson_data(
                    change.old,
                    change.new,
                    now=now,
                    mais_group_id=mais_group_id,
                )

            # UNCHANGED
            for change in diff.unchanged:
                assert change.old is not None
                change.old.last_seen_at = now

            # DELETED
            for change in diff.deleted:
                assert change.old is not None
                session.delete(change.old)

            session.commit()

            # Synchronize changes to Google Calendar if a service is provided.
            if self.google_calendar_service is not None:
                self.google_calendar_service.sync_changes(diff)

            # Update statistics and gamification
            self._update_stats(
                len(incoming),
                user_id=user_id,
            )

            return SyncResult(
                parsed=len(incoming),
                created=len(diff.created),
                updated=len(diff.updated),
                moved=len(diff.moved),
                deleted=len(diff.deleted),
                unchanged=len(diff.unchanged),
                diff=diff,
            )

    def get_stats(self, user_id: int) -> UserStats:
        """
        Get user statistics and gamification data.
        Returns the UserStats object.
        """
        with self.db.session() as session:
            stats = (
                session.query(UserStats).filter(UserStats.user_id == user_id).first()
            )

            if not stats:
                stats = UserStats(
                    user_id=user_id,
                    level=1,
                    max_streak=0,
                )
                session.add(stats)
                session.commit()

            return stats
