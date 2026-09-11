from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from zoneinfo import ZoneInfo

from app.database.models import Lesson
from app.ics.parser import LessonData


LOCAL_TIMEZONE = ZoneInfo("Europe/Moscow")


@dataclass(frozen=True, slots=True)
class LessonChange:
    """
    Результат сравнения одного занятия.

    kind:
        CREATED
        UPDATED
        MOVED
        DELETED
        UNCHANGED

    score:
        Уверенность fuzzy-сопоставления.
        Для exact match значение равно 100.
    """

    kind: str
    stable_id: str

    old: Lesson | None
    new: LessonData | None

    score: int = 100

    @property
    def description(self) -> str:
        """Человекочитаемое описание изменения."""
        def fmt(dt: datetime) -> str:
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=LOCAL_TIMEZONE)
            return dt.astimezone(LOCAL_TIMEZONE).strftime("%d.%m.%Y %H:%M")

        if self.kind == "CREATED":
            assert self.new is not None
            return f"Создано: {self.new.subject} ({self.new.lesson_type}) {fmt(self.new.start_time)} - {fmt(self.new.end_time)}"
        if self.kind == "DELETED":
            assert self.old is not None
            return f"Удалено: {self.old.subject} ({self.old.lesson_type}) {fmt(self.old.start_time)} - {fmt(self.old.end_time)}"
        if self.kind == "UPDATED":
            assert self.old is not None and self.new is not None
            return f"Обновлено: {self.new.subject} ({self.new.lesson_type}) {fmt(self.new.start_time)} - {fmt(self.new.end_time)}"
        if self.kind == "MOVED":
            assert self.old is not None and self.new is not None
            return f"Перенесено: {self.new.subject} ({self.new.lesson_type}) с {fmt(self.old.start_time)} - {fmt(self.old.end_time)} на {fmt(self.new.start_time)} - {fmt(self.new.end_time)}"
        return f"Неизвестное изменение: {self.kind}"


@dataclass(frozen=True, slots=True)
class DiffResult:
    created: tuple[LessonChange, ...]
    updated: tuple[LessonChange, ...]
    moved: tuple[LessonChange, ...]
    deleted: tuple[LessonChange, ...]
    unchanged: tuple[LessonChange, ...]

    @property
    def changes(self) -> tuple[LessonChange, ...]:
        return (
            self.created
            + self.updated
            + self.moved
            + self.deleted
        )


def _as_local(value: datetime) -> datetime:
    """
    Приводит datetime к Europe/Moscow.

    SQLite может вернуть datetime без tzinfo даже если
    модель использует DateTime(timezone=True).

    Поэтому здесь нормализуем оба варианта.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=LOCAL_TIMEZONE)

    return value.astimezone(LOCAL_TIMEZONE)


def _same_datetime(
    left: datetime,
    right: datetime,
) -> bool:
    return _as_local(left) == _as_local(right)


def _same_date(
    left: datetime,
    right: datetime,
) -> bool:
    return (
        _as_local(left).date()
        == _as_local(right).date()
    )


def _date_distance_days(
    left: datetime,
    right: datetime,
) -> int:
    return abs(
        (
            _as_local(left).date()
            - _as_local(right).date()
        ).days
    )


def _lesson_score(
    old: Lesson,
    new: LessonData,
) -> int:
    """
    Оценивает вероятность того, что old и new —
    одно и то же занятие после изменения расписания.

    Максимум для записи на ту же дату: 100.

    Для занятия, перенесённого на другую дату,
    дата не даёт баллов, поэтому максимум — 85.

    Это специально консервативный алгоритм:
    лучше показать DELETE + CREATE, чем ошибочно
    объединить две разные пары.
    """
    score = 0

    if old.subject.casefold() == new.subject.casefold():
        score += 35

    if old.category == new.category:
        score += 15

    if old.lesson_type == new.lesson_type:
        score += 10

    if (
        old.teacher
        and new.teacher
        and old.teacher.casefold()
        == new.teacher.casefold()
    ):
        score += 15

    if (
        old.room
        and new.room
        and old.room.casefold()
        == new.room.casefold()
    ):
        score += 10

    if _same_date(
        old.start_time,
        new.start_time,
    ):
        score += 15

    return score


def _find_best_match(
    old_lessons: Iterable[Lesson],
    new: LessonData,
) -> tuple[Lesson | None, int]:
    """
    Ищет лучшее fuzzy-сопоставление.

    Ограничиваем поиск 14 днями, чтобы не сопоставить
    одну неделю семестрового расписания с такой же
    парой через несколько месяцев.
    """
    candidates: list[tuple[int, Lesson]] = []

    for old in old_lessons:
        if _date_distance_days(
            old.start_time,
            new.start_time,
        ) > 14:
            continue

        score = _lesson_score(old, new)

        if score >= 70:
            candidates.append((score, old))

    if not candidates:
        return None, 0

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best = candidates[0]

    # Если есть второй почти такой же кандидат,
    # автоматически выбирать нельзя.
    if len(candidates) > 1:
        second_score = candidates[1][0]

        if best_score - second_score < 15:
            return None, 0

    return best, best_score


def calculate_diff(
    old_lessons: Iterable[Lesson],
    new_lessons: Iterable[LessonData],
) -> DiffResult:
    """
    Сравнивает старое состояние с новым.

    Алгоритм:

    1. Exact match по identity_key.
    2. Для оставшихся записей fuzzy matching.
    3. Остатки классифицируются как CREATED/DELETED.
    """
    old_list = list(old_lessons)
    new_list = list(new_lessons)

    old_by_identity = {
        lesson.stable_id: lesson
        for lesson in old_list
    }

    new_by_identity = {
        lesson.identity_key: lesson
        for lesson in new_list
    }

    matched_old_ids: set[int] = set()
    matched_new_ids: set[str] = set()

    created: list[LessonChange] = []
    updated: list[LessonChange] = []
    moved: list[LessonChange] = []
    deleted: list[LessonChange] = []
    unchanged: list[LessonChange] = []

    # ---------------------------------------------------------
    # 1. EXACT MATCH
    # ---------------------------------------------------------

    for stable_id, new in new_by_identity.items():
        old = old_by_identity.get(stable_id)

        if old is None:
            continue

        matched_old_ids.add(old.id)
        matched_new_ids.add(stable_id)

        if old.content_hash == new.content_hash:
            unchanged.append(
                LessonChange(
                    kind="UNCHANGED",
                    stable_id=stable_id,
                    old=old,
                    new=new,
                    score=100,
                )
            )
            continue

        updated.append(
            LessonChange(
                kind="UPDATED",
                stable_id=stable_id,
                old=old,
                new=new,
                score=100,
            )
        )

    # ---------------------------------------------------------
    # 2. FUZZY MATCH
    # ---------------------------------------------------------

    unmatched_old = [
        lesson
        for lesson in old_list
        if lesson.id not in matched_old_ids
    ]

    unmatched_new = [
        lesson
        for lesson in new_list
        if lesson.identity_key not in matched_new_ids
    ]

    for new in unmatched_new:
        available_old = [
            old
            for old in unmatched_old
            if old.id not in matched_old_ids
        ]

        old, score = _find_best_match(
            available_old,
            new,
        )

        if old is None:
            created.append(
                LessonChange(
                    kind="CREATED",
                    stable_id=new.identity_key,
                    old=None,
                    new=new,
                    score=0,
                )
            )
            continue

        matched_old_ids.add(old.id)
        matched_new_ids.add(new.identity_key)

        if (
            _same_datetime(
                old.start_time,
                new.start_time,
            )
            and _same_datetime(
                old.end_time,
                new.end_time,
            )
        ):
            updated.append(
                LessonChange(
                    kind="UPDATED",
                    stable_id=old.stable_id,
                    old=old,
                    new=new,
                    score=score,
                )
            )
        else:
            moved.append(
                LessonChange(
                    kind="MOVED",
                    stable_id=old.stable_id,
                    old=old,
                    new=new,
                    score=score,
                )
            )

    # ---------------------------------------------------------
    # 3. DELETE
    # ---------------------------------------------------------

    for old in old_list:
        if old.id in matched_old_ids:
            continue

        deleted.append(
            LessonChange(
                kind="DELETED",
                stable_id=old.stable_id,
                old=old,
                new=None,
                score=0,
            )
        )

    return DiffResult(
        created=tuple(created),
        updated=tuple(updated),
        moved=tuple(moved),
        deleted=tuple(deleted),
        unchanged=tuple(unchanged),
    )