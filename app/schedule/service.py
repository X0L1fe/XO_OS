from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.common.schedule_filters import (
    SCHEDULE_CATEGORY_LABELS,
    get_schedule_exclusions,
    lesson_is_excluded_by_category,
    lesson_is_excluded_by_subject,
    lesson_is_visible,
    normalize_schedule_category,
    normalize_schedule_value,
)
from app.database.models import Lesson, ScheduleExclusion, User


class ScheduleService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_filter_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get the user's schedule filter data for the GET endpoint.
        Returns the same structure as the old get_schedule_filters endpoint.
        """
        # Get lessons for the user to determine available categories and subjects
        lessons = (
            self.db.query(Lesson)
            .filter(Lesson.user_id == user_id)
            .order_by(Lesson.subject.asc())
            .all()
        )

        # Get current exclusions
        excluded_categories, excluded_subjects = get_schedule_exclusions(
            self.db, user_id
        )

        # Build available categories from lessons and always show core categories
        available_categories: Set[str] = set()
        for lesson in lessons:
            available_categories.add(normalize_schedule_category(lesson.category))
        for category in SCHEDULE_CATEGORY_LABELS:
            available_categories.add(category)

        # Build categories list for response
        categories = []
        for category in ["REGULAR", "ELECTIVE", "MILITARY"]:
            if category in available_categories:
                categories.append(
                    {
                        "key": category,
                        "label": SCHEDULE_CATEGORY_LABELS[category],
                        "excluded": category in excluded_categories,
                    }
                )

        # Build subjects list from lessons
        subjects_by_key: Dict[str, str] = {}
        for lesson in lessons:
            if not lesson.subject:
                continue
            label = " ".join(lesson.subject.strip().split())
            key = normalize_schedule_value(label)
            if not key:
                continue
            if key not in subjects_by_key:
                subjects_by_key[key] = label

        subjects = [
            {
                "key": key,
                "label": label,
                "excluded": key in excluded_subjects,
            }
            for key, label in sorted(
                subjects_by_key.items(), key=lambda item: item[1].lower()
            )
        ]

        return {
            "excluded_categories": sorted(excluded_categories),
            "excluded_subjects": sorted(excluded_subjects),
            "categories": categories,
            "subjects": subjects,
        }

    def update_filters(
        self,
        user_id: int,
        excluded_categories: List[str],
        excluded_subjects: List[str],
    ) -> Dict[str, Any]:
        """
        Update the user's schedule exclusions.
        Returns the same structure as the old update_schedule_filters endpoint.
        """
        # Delete existing exclusions for this user
        self.db.query(ScheduleExclusion).filter(
            ScheduleExclusion.user_id == user_id
        ).delete()

        # Normalize and filter categories
        categories_set: Set[str] = set()
        for value in excluded_categories:
            if value:
                normalized = normalize_schedule_category(value)
                if normalized in {"REGULAR", "ELECTIVE", "MILITARY"}:
                    categories_set.add(normalized)

        # Normalize subjects
        subjects_set: Set[str] = set()
        for value in excluded_subjects:
            if value:
                normalized = normalize_schedule_value(value)
                if normalized:
                    subjects_set.add(normalized)

        # Build label maps for categories and subjects
        category_labels = {k: v for k, v in SCHEDULE_CATEGORY_LABELS.items()}

        # Get lessons to build subject labels map
        lessons = self.db.query(Lesson).filter(Lesson.user_id == user_id).all()
        subject_labels: Dict[str, str] = {}
        for lesson in lessons:
            if not lesson.subject:
                continue
            normalized = normalize_schedule_value(lesson.subject)
            if normalized and normalized not in subject_labels:
                subject_labels[normalized] = lesson.subject.strip()

        # Add category exclusions
        for category in sorted(categories_set):
            self.db.add(
                ScheduleExclusion(
                    user_id=user_id,
                    exclusion_type="category",
                    value_key=category,
                    value_label=category_labels.get(category, category),
                )
            )

        # Add subject exclusions
        for subject_key in sorted(subjects_set):
            self.db.add(
                ScheduleExclusion(
                    user_id=user_id,
                    exclusion_type="subject",
                    value_key=subject_key,
                    value_label=subject_labels.get(subject_key, subject_key),
                )
            )

        self.db.commit()

        return {
            "success": True,
            "excluded_categories": sorted(categories_set),
            "excluded_subjects": sorted(subjects_set),
        }

    def get_today_schedule(
        self,
        user_id: int,
        mode: str = "today",
    ) -> List[Dict[str, Any]]:
        """
        mode="today" — только сегодняшние занятия;
        mode="all"   — всё расписание пользователя.
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Get user's schedule exclusions
        excluded_categories, excluded_subjects = get_schedule_exclusions(
            self.db, user_id
        )

        query = self.db.query(Lesson).filter(Lesson.user_id == user_id)
        # Query lessons for today
        if mode == "today":
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            query = query.filter(
                Lesson.start_time >= today_start,
                Lesson.start_time <= today_end,
            )

        lessons = query.order_by(Lesson.start_time).all()

        result: List[Dict[str, Any]] = []

        for lesson in lessons:
            # Check if lesson is visible (not excluded)
            if not lesson_is_visible(
                lesson,
                excluded_categories,
                excluded_subjects,
            ):
                continue

            # Normalize category for display
            category = normalize_schedule_category(lesson.category)

            result.append(
                {
                    "id": lesson.id,
                    "stable_id": lesson.stable_id,
                    "date": lesson.start_time.date().isoformat(),
                    "time": lesson.start_time.strftime("%H:%M"),
                    "end_time": (
                        lesson.end_time.strftime("%H:%M") if lesson.end_time else None
                    ),
                    "subject": lesson.subject,
                    "type": lesson.lesson_type,
                    "category": category,
                    "room": lesson.room or "",
                    "teacher": lesson.teacher or "",
                    "status": ("sync" if lesson.google_event_id else "unsynced"),
                }
            )

        return result
