from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.service import get_current_active_user
from app.common.time import msk_now_naive
from app.database.db import db
from app.database.models import Lesson, ScheduleExclusion, User, UserStats
from app.stats.service import (
    clipped_lesson_duration_hours,
    get_filtered_semester_lessons,
    get_schedule_exclusions,
    get_semester_bounds,
    lesson_duration_hours,
    lesson_is_visible,
    normalize_schedule_category,
    normalize_schedule_value,
)

router = APIRouter()


@router.get("/stats/semester")
def get_semester_stats(current_user: User = Depends(get_current_active_user)):
    """
    Загрузка семестра в фактических часах.

    Фильтры применяются перед расчетом.
    """

    now = msk_now_naive()

    with db.session() as session:
        result = get_filtered_semester_lessons(
            session,
            current_user,
            now,
        )

        if result is None:
            return {
                "lecture": 0,
                "practice": 0,
                "lab": 0,
                "other": 0,
                "total": 0,
                "lesson_count": 0,
            }

        lessons, semester_start, semester_end = result

        hours_by_type = {
            "lecture": 0.0,
            "practice": 0.0,
            "lab": 0.0,
            "other": 0.0,
        }

        for lesson in lessons:
            hours = lesson_duration_hours(lesson)

            lesson_type = normalize_schedule_value(lesson.lesson_type)

            if lesson_type == "LECTURE":
                hours_by_type["lecture"] += hours

            elif lesson_type == "PRACTICE":
                hours_by_type["practice"] += hours

            elif lesson_type == "LAB":
                hours_by_type["lab"] += hours

            else:
                hours_by_type["other"] += hours

        total = sum(hours_by_type.values())

        return {
            "lecture": round(
                hours_by_type["lecture"],
                2,
            ),
            "practice": round(
                hours_by_type["practice"],
                2,
            ),
            "lab": round(
                hours_by_type["lab"],
                2,
            ),
            "other": round(
                hours_by_type["other"],
                2,
            ),
            "total": round(total, 2),
            "lesson_count": len(lessons),
        }


@router.get("/stats/weekly")
def get_weekly_stats(current_user: User = Depends(get_current_active_user)):
    """
    Загруженность по каждой неделе текущего семестра.

    Будущие недели возвращаются с 0 часами, поэтому интерфейс
    может отображать полную шкалу семестра.
    """

    now = msk_now_naive()

    with db.session() as session:
        result = get_filtered_semester_lessons(
            session,
            current_user,
            now,
        )

        if result is None:
            return []

        lessons, semester_start, semester_end = result

        # First week starts on Monday.
        first_week_start = semester_start - timedelta(days=semester_start.weekday())

        # Make sure we do not start before semester.
        first_week_start = max(
            first_week_start,
            semester_start,
        )

        weeks = []

        cursor = first_week_start
        week_number = 1

        while cursor <= semester_end:
            week_start = cursor
            week_end = min(
                cursor + timedelta(days=7),
                semester_end + timedelta(seconds=1),
            )

            hours = 0.0

            for lesson in lessons:
                hours += clipped_lesson_duration_hours(
                    lesson,
                    week_start,
                    week_end,
                )

            current_week = week_start <= now < week_end

            weeks.append(
                {
                    "week": week_number,
                    "label": str(week_number),
                    "date_start": week_start.strftime("%d.%m"),
                    "date_end": (week_end - timedelta(seconds=1)).strftime("%d.%m"),
                    "hours": round(hours, 2),
                    "current": current_week,
                }
            )

            cursor += timedelta(days=7)
            week_number += 1

        return weeks


@router.get("/stats/topsubjects")
def get_top_subjects(current_user: User = Depends(get_current_active_user)):
    """
    Лучшие предметы по фактической учебной нагрузке в семестре.

    Фильтры применяются перед агрегацией.
    """

    now = msk_now_naive()

    with db.session() as session:
        result = get_filtered_semester_lessons(
            session,
            current_user,
            now,
        )

        if result is None:
            return []

        lessons, semester_start, semester_end = result

        subject_stats = {}

        for lesson in lessons:
            subject = (lesson.subject or "Без названия").strip()

            if not subject:
                subject = "Без названия"

            if subject not in subject_stats:
                subject_stats[subject] = {
                    "hours": 0.0,
                    "lessons": 0,
                }

            subject_stats[subject]["hours"] += lesson_duration_hours(lesson)

            subject_stats[subject]["lessons"] += 1

        sorted_subjects = sorted(
            subject_stats.items(),
            key=lambda item: item[1]["hours"],
            reverse=True,
        )[:5]

        return [
            {
                "name": subject,
                "hours": round(
                    values["hours"],
                    2,
                ),
                "lessons": values["lessons"],
            }
            for subject, values in sorted_subjects
        ]


@router.get("/stats/planfact")
def get_plan_fact(current_user: User = Depends(get_current_active_user)):
    """
    Ход семестра.

    Старая конечная точка не возвращала заполнителей.
    Теперь мы отображаем фактические истекшие и оставшиеся запланированные
    нагрузка после применения фильтров.

    завершено = часть запланированных часов урока, которая была
                уже прошло.
    осталось = часть еще впереди.
    """

    now = msk_now_naive()

    with db.session() as session:
        result = get_filtered_semester_lessons(
            session,
            current_user,
            now,
        )

        if result is None:
            return {
                "total": 0,
                "completed": 0,
                "remaining": 0,
                "progress_percent": 0,
            }

        lessons, semester_start, semester_end = result

        total = 0.0
        completed = 0.0

        for lesson in lessons:
            total += lesson_duration_hours(lesson)

            completed += clipped_lesson_duration_hours(
                lesson,
                semester_start,
                min(now, semester_end),
            )

        completed = min(completed, total)
        remaining = max(total - completed, 0.0)

        progress_percent = (completed / total) * 100 if total > 0 else 0.0

        return {
            "total": round(total, 2),
            "completed": round(completed, 2),
            "remaining": round(remaining, 2),
            "progress_percent": round(
                progress_percent,
                1,
            ),
        }


@router.get("/achievements")
def get_achievements(current_user: User = Depends(get_current_active_user)):
    """Get achievements based on stats."""
    with db.session() as session:
        stats = (
            session.query(UserStats)
            .filter(UserStats.user_id == current_user.id)
            .first()
        )
        if not stats:
            stats = UserStats(user_id=current_user.id)
            session.add(stats)
            session.commit()
        achievements = []
        # Streak achievements
        if stats.current_streak >= 7:
            achievements.append(f"Стаж {stats.current_streak} дней")
        if stats.current_streak >= 30:
            achievements.append(f"Стаж {stats.current_streak} дней")
        # Level achievements
        if stats.level >= 1:
            achievements.append(f"Уровень {stats.level}")
        if stats.level >= 5:
            achievements.append(f"Уровень {stats.level}")
        if stats.level >= 10:
            achievements.append(f"Уровень {stats.level}")
        # XP achievements
        if stats.total_xp >= 1000:
            achievements.append("Новичок")
        if stats.total_xp >= 5000:
            achievements.append("Опытный")
        if stats.total_xp >= 10000:
            achievements.append("Ветеран")
        return {"achievements": achievements, "streak": stats.current_streak}
