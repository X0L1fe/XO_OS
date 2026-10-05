from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.common.schedule_filters import (
    get_schedule_exclusions,
    lesson_is_excluded_by_category,
    lesson_is_excluded_by_subject,
    lesson_is_visible,
    normalize_schedule_category,
    normalize_schedule_value,
)
from app.common.time import msk_now_naive
from app.database.models import Lesson, ScheduleExclusion, User


def get_semester_bounds(
    now: datetime,
) -> Optional[Tuple[datetime, datetime]]:
    """
    Получение текущих границ академического семестра.

    Возвращает naive MSK-время, потому что Lesson.start_time / Lesson.end_time
    в БД хранятся как naive MSK. Сравнения работают только в одной шкале.

    Текущее соглашение проекта:
        Весна-лето: 1 февраля – 31 мая.
        Осень-зима: 1 сентября – 31 декабря.

    Возвращает None в течение июня-августа и января.
    """

    if 2 <= now.month <= 6:
        return (
            datetime(now.year, 2, 1),
            datetime(now.year, 5, 31, 23, 59, 59),
        )

    if 9 <= now.month <= 12:
        return (
            datetime(now.year, 9, 1),
            datetime(now.year, 12, 31, 23, 59, 59),
        )

    return None


def lesson_duration_hours(
    lesson: Lesson,
) -> float:
    """
    Продолжительность занятий возврата в часах.
    """

    if not lesson.start_time or not lesson.end_time:
        return 0.0

    start = lesson.start_time
    end = lesson.end_time

    return max(
        (end - start).total_seconds() / 3600.0,
        0.0,
    )


def clipped_lesson_duration_hours(
    lesson: Lesson,
    start: datetime,
    end: datetime,
) -> float:
    """
    Часть продолжительности урока, попавшая в интервал [start, end].
    """
    if not lesson.start_time or not lesson.end_time:
        return 0.0

    clipped_start = max(lesson.start_time, start)
    clipped_end = min(lesson.end_time, end)

    if clipped_end <= clipped_start:
        return 0.0

    return (clipped_end - clipped_start).total_seconds() / 3600.0


def get_filtered_semester_lessons(
    session: Session,
    current_user: User,
    now: Optional[datetime] = None,
) -> Optional[Tuple[List[Lesson], datetime, datetime]]:
    """
    Получить все видимые уроки в текущем семестре.

    Это общий источник статистики семестра.
    """

    if now is None:
        now = msk_now_naive()

    bounds = get_semester_bounds(now)

    if bounds is None:
        return None

    semester_start, semester_end = bounds

    excluded_categories, excluded_subjects = get_schedule_exclusions(
        session,
        current_user.id,
    )

    lessons = (
        session.query(Lesson)
        .filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= semester_start,
            Lesson.start_time <= semester_end,
        )
        .order_by(Lesson.start_time)
        .all()
    )

    visible_lessons = [
        lesson
        for lesson in lessons
        if lesson_is_visible(
            lesson,
            excluded_categories,
            excluded_subjects,
        )
    ]

    return (
        visible_lessons,
        semester_start,
        semester_end,
    )
