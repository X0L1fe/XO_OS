"""Единый источник времени для всего проекта."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

MAI_TZ = ZoneInfo("Europe/Moscow")


def utc_now() -> datetime:
    """Aware UTC. Для ВСЕЙ логики: фокус-сессии, XP, фоновые задачи,
    транзакции, last_activity_date, интервалы внутри процесса."""
    return datetime.now(timezone.utc)


def msk_now_naive() -> datetime:
    """Naive MSK. ТОЛЬКО для сравнения с Lesson.start_time / Lesson.end_time,
    которые хранятся в БД как наивное московское время."""
    return datetime.now(MAI_TZ).replace(tzinfo=None)
