from __future__ import annotations

from typing import Set, Tuple
from sqlalchemy.orm import Session

from app.database.models import Lesson, ScheduleExclusion


def normalize_schedule_value(value: str | None) -> str:
    """
    Normalize a schedule value for comparison.

    Example:
        "  Программирование  " -> "ПРОГРАММИРОВАНИЕ"
    """
    if not value:
        return ""
    return " ".join(value.strip().split()).upper()


def normalize_schedule_category(value: str | None) -> str:
    """
    Normalize lesson category.
    Empty category is treated as REGULAR.
    """
    normalized = normalize_schedule_value(value)

    if not normalized:
        return "REGULAR"

    if normalized in {
        "MILITARY",
        "ВОЕННАЯ",
        "ВОЕННАЯ ПОДГОТОВКА",
    }:
        return "MILITARY"

    if normalized in {
        "ELECTIVE",
        "ЭЛЕКТИВ",
        "ЭЛЕКТИВЫ",
    }:
        return "ELECTIVE"

    if normalized in {
        "REGULAR",
        "ОБЫЧНЫЕ",
        "ОБЫЧНЫЕ ЗАНЯТИЯ",
    }:
        return "REGULAR"

    return normalized


def lesson_is_visible(
    lesson: Lesson,
    excluded_categories: Set[str],
    excluded_subjects: Set[str],
) -> bool:
    """
    Return True when lesson should be included in schedule/statistics.
    """
    category = normalize_schedule_category(lesson.category)
    subject = normalize_schedule_value(lesson.subject)

    if category in excluded_categories:
        return False

    if subject and subject in excluded_subjects:
        return False

    return True


def lesson_is_excluded_by_category(
    lesson: Lesson,
    excluded_categories: Set[str],
) -> bool:
    """Check if lesson is excluded by category."""
    return normalize_schedule_category(lesson.category) in excluded_categories


def lesson_is_excluded_by_subject(
    lesson: Lesson,
    excluded_subjects: Set[str],
) -> bool:
    """Check if lesson is excluded by subject."""
    subject = normalize_schedule_value(lesson.subject)
    return subject and subject in excluded_subjects


def get_schedule_exclusions(
    session: Session,
    user_id: int,
) -> Tuple[Set[str], Set[str]]:
    """
    Get the user's schedule exclusions as sets of normalized category and subject values.
    Returns (excluded_categories, excluded_subjects).
    """
    exclusions = (
        session.query(ScheduleExclusion)
        .filter(ScheduleExclusion.user_id == user_id)
        .all()
    )

    excluded_categories: Set[str] = set()
    excluded_subjects: Set[str] = set()

    for exclusion in exclusions:
        if exclusion.exclusion_type == "category":
            excluded_categories.add(normalize_schedule_category(exclusion.value_key))
        elif exclusion.exclusion_type == "subject":
            excluded_subjects.add(normalize_schedule_value(exclusion.value_key))

    return excluded_categories, excluded_subjects