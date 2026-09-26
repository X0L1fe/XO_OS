from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Set

from app.database.models import User, Lesson, ScheduleExclusion
from app.common.schedule_filters import (
    normalize_schedule_value,
    normalize_schedule_category,
    lesson_is_visible,
    lesson_is_excluded_by_category,
    lesson_is_excluded_by_subject,
    get_schedule_exclusions,
)










def get_semester_bounds(
    now: datetime,
) -> Optional[Tuple[datetime, datetime]]:
    """
    Получение текущие границы академического семестра.

    Текущее соглашение проекта:
        Весна-лето: 1 февраля – 31 мая.
        Осень-зима: 1 сентября – 31 декабря.

    Возвращает None в течение июня-августа и января.
    """

    if 2 <= now.month <= 6:
        return (
            datetime(
                now.year,
                2,
                1,
                tzinfo=timezone.utc,
            ),
            datetime(
                now.year,
                5,
                31,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            ),
        )

    if 9 <= now.month <= 12:
        return (
            datetime(
                now.year,
                9,
                1,
                tzinfo=timezone.utc,
            ),
            datetime(
                now.year,
                12,
                31,
                23,
                59,
                59,
                tzinfo=timezone.utc,
            ),
        )

    return None


def _as_aware_utc(value: datetime) -> datetime:
    """
    Нормализация времени к UTC формату для сравнения из БД
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def lesson_duration_hours(
    lesson: Lesson,
) -> float:
    """
    Продолжительность занятий возврата в часах.
    """

    if not lesson.start_time or not lesson.end_time:
        return 0.0

    start = _as_aware_utc(lesson.start_time)
    end = _as_aware_utc(lesson.end_time)

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
    Рассчитать только ту часть продолжительности урока, которая лежит
    внутри [start, end].
    """

    if not lesson.start_time or not lesson.end_time:
        return 0.0

    lesson_start = _as_aware_utc(lesson.start_time)
    lesson_end = _as_aware_utc(lesson.end_time)

    bound_start = _as_aware_utc(start)
    bound_end = _as_aware_utc(end)

    clipped_start = max(lesson_start, bound_start)
    clipped_end = min(lesson_end, bound_end)

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
        now = datetime.now(timezone.utc)

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