from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from app.ics.parser import LessonData
from app.sync.diff import calculate_diff


MSK = ZoneInfo("Europe/Moscow")


def make_old(
    *,
    lesson_id: int = 1,
    stable_id: str = "old-id",
    date_day: int = 5,
    start_hour: int = 13,
    start_minute: int = 0,
):
    start = datetime(
        2026,
        9,
        date_day,
        start_hour,
        start_minute,
        tzinfo=MSK,
    )

    end = start + timedelta(minutes=90)

    return SimpleNamespace(
        id=lesson_id,
        stable_id=stable_id,
        source_uid="old-uid",

        subject="Теория графов",
        lesson_type="LECTURE",
        category="REGULAR",

        start_time=start,
        end_time=end,

        teacher="ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА",
        room="ГУК В-214",

        content_hash="old-hash",
    )


def make_new(
    *,
    date_day: int = 5,
    start_hour: int = 13,
    start_minute: int = 0,
    identity_key: str = "new-id",
    content_hash: str = "new-hash",
):
    start = datetime(
        2026,
        9,
        date_day,
        start_hour,
        start_minute,
        tzinfo=MSK,
    )

    end = start + timedelta(minutes=90)

    return LessonData(
        source_uid="new-uid",
        identity_key=identity_key,

        subject="Теория графов",
        lesson_type="LECTURE",
        category="REGULAR",

        start_time=start,
        end_time=end,

        teacher="ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА",
        teachers=(
            "ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА",
        ),

        room="ГУК В-214",

        description=(
            "ЛК: ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА"
        ),

        raw_ics="",
    )


def test_exact_identity_is_updated():
    old = make_old(
        stable_id="same-id",
    )

    new = make_new(
        identity_key="same-id",
    )

    result = calculate_diff(
        [old],
        [new],
    )

    assert len(result.updated) == 1
    assert len(result.moved) == 0
    assert len(result.created) == 0
    assert len(result.deleted) == 0


def test_time_change_is_moved():
    old = make_old(
        date_day=5,
        start_hour=13,
        start_minute=0,
    )

    new = make_new(
        date_day=5,
        start_hour=14,
        start_minute=45,
    )

    result = calculate_diff(
        [old],
        [new],
    )

    assert len(result.moved) == 1
    assert len(result.created) == 0
    assert len(result.deleted) == 0

    change = result.moved[0]

    assert change.old is old
    assert change.new is new
    assert change.score >= 70


def test_date_change_is_moved():
    old = make_old(
        date_day=5,
        start_hour=13,
    )

    new = make_new(
        date_day=7,
        start_hour=13,
    )

    result = calculate_diff(
        [old],
        [new],
    )

    assert len(result.moved) == 1
    assert len(result.created) == 0
    assert len(result.deleted) == 0


def test_new_lesson_is_created():
    old = make_old()

    new = make_new(
        date_day=6,
        start_hour=9,
    )

    new = replace(
        new,
        subject="Программирование",
        teacher="Петров П.П.",
        teachers=("Петров П.П.",),
        description="ЛК: Петров П.П.",
    )

    result = calculate_diff(
        [old],
        [new],
    )

    assert len(result.created) == 1
    assert len(result.moved) == 0
    assert len(result.deleted) == 1


def test_unchanged_lesson_is_unchanged():
    old = make_old(
        stable_id="same-id",
    )

    new = make_new(
        identity_key="same-id",
    )

    old_hash = new.content_hash

    old.content_hash = old_hash

    result = calculate_diff(
        [old],
        [new],
    )

    assert len(result.unchanged) == 1
    assert len(result.updated) == 0
    assert len(result.moved) == 0
    assert len(result.created) == 0
    assert len(result.deleted) == 0