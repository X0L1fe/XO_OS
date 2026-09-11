from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from icalendar import Calendar


MAI_TIMEZONE = ZoneInfo("Europe/Moscow")


LESSON_TYPE_MAP = {
    "ЛК": "LECTURE",
    "ПЗ": "PRACTICE",
    "ЛР": "LAB",
    "Э": "EXAM",
}


@dataclass(frozen=True, slots=True)
class LessonData:
    """
    Нормализованное занятие MAISync.

    source_uid:
        Оригинальный UID из ICS. Сохраняем для отладки и трассировки,
        но НЕ используем как identity между разными экспортами.

    identity_key:
        Наш собственный идентификатор конкретного занятия.

    teachers:
        Все преподаватели занятия.

    teacher:
        Первый преподаватель для обратной совместимости и удобства.
    """

    source_uid: str | None
    identity_key: str

    subject: str
    lesson_type: str
    category: str

    start_time: datetime
    end_time: datetime

    teacher: str | None
    teachers: tuple[str, ...]

    room: str | None
    description: str | None

    raw_ics: str

    @property
    def stable_id(self) -> str:
        """
        Совместимость с предыдущей версией проекта.

        В будущем лучше везде перейти на identity_key.
        """
        return self.identity_key

    @property
    def content_hash(self) -> str:
        """
        Хэш всех изменяемых данных занятия.

        Если хэш поменялся — занятие необходимо обновить.
        """
        raw = "\n".join(
            [
                self.subject,
                self.lesson_type,
                self.category,
                self.start_time.isoformat(),
                self.end_time.isoformat(),
                "|".join(self.teachers),
                self.room or "",
                self.description or "",
            ]
        )

        return hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()


def _text(value: Any) -> str:
    """
    Безопасно преобразует значение ICS в строку.

    Значения ICS могут содержать escape-последовательности,
    которые приводятся к обычному тексту.
    """
    if value is None:
        return ""

    if hasattr(value, "to_ical"):
        value = value.to_ical().decode(
            "utf-8",
            errors="replace",
        )
    else:
        value = str(value)

    # RFC 5545 escape sequences.
    value = value.replace(r"\,", ",")
    value = value.replace(r"\;", ";")
    value = value.replace(r"\n", "\n")
    value = value.replace(r"\N", "\n")
    value = value.replace(r"\\", "\\")

    return value


def _clean(value: str | None) -> str | None:
    """
    Нормализует пробелы и пустые значения.
    """
    if not value:
        return None

    value = " ".join(value.split())

    return value or None


def _parse_datetime(value: Any) -> datetime:
    """
    Преобразует DTSTART/DTEND в timezone-aware datetime.

    В реальном ICS МАИ дата приходит без TZID/Z:
        DTSTART:20260905T130000

    Поэтому интерпретируем её как Europe/Moscow.
    """
    if value is None:
        raise ValueError(
            "VEVENT does not contain required datetime field"
        )

    dt = value.dt

    if not isinstance(dt, datetime):
        raise ValueError(
            "Only datetime DTSTART/DTEND are supported"
        )

    if dt.tzinfo is None:
        return dt.replace(tzinfo=MAI_TIMEZONE)

    return dt.astimezone(MAI_TIMEZONE)


def _parse_description(
    description: str,
) -> tuple[str, tuple[str, ...]]:
    """
    Разбирает DESCRIPTION МАИ.

    Обычный пример:

        ЛК: Чечиков Юрий Борисович

    Несколько преподавателей:

        ЛР: Бурова Аделия Юрьевна, Версин Александр Андреевич

    Составной вариант:

        Военная подготовка(ПЗ): ;
        Занятие в группах индивидуальных траекторий.(ПЗ):
    """
    if not description:
        return "OTHER", ()

    lesson_types: list[str] = []
    teachers: list[str] = []

    # Обычный формат:
    # ЛК: Иванов И.И.
    # ПЗ: Петров П.П.
    # ЛР: Иванов И.И., Петров П.П.
    for match in re.finditer(
        r"(?P<label>[А-ЯЁA-Z]{1,4})\s*:\s*(?P<teacher>[^;\n]*)",
        description,
        flags=re.IGNORECASE,
    ):
        label = match.group("label").upper()

        mapped_type = LESSON_TYPE_MAP.get(label)

        if mapped_type is None:
            continue

        lesson_types.append(mapped_type)

        teacher = _clean(match.group("teacher"))

        if teacher:
            teachers.extend(
                part.strip()
                for part in teacher.split(",")
                if part.strip()
            )

    # Составной формат:
    #
    # Военная подготовка(ПЗ):
    #
    # В нём тип занятия находится в скобках.
    for match in re.finditer(
        r"\((ЛК|ПЗ|ЛР|Э)\)",
        description,
        flags=re.IGNORECASE,
    ):
        lesson_types.append(
            LESSON_TYPE_MAP[
                match.group(1).upper()
            ]
        )

    # Первый найденный тип считаем основным.
    lesson_type = (
        lesson_types[0]
        if lesson_types
        else "OTHER"
    )

    # Убираем дубликаты, сохраняя порядок.
    unique_teachers = tuple(
        dict.fromkeys(teachers)
    )

    return lesson_type, unique_teachers


def _detect_category(
    subject: str,
    description: str,
) -> str:
    """
    Определяет категорию занятия.

    REGULAR  — обычное занятие
    ELECTIVE — электив
    MILITARY  — военная подготовка
    """
    text = f"{subject} {description}".casefold()

    if (
        "военная подготовка" in text
        or "военная кафедра" in text
    ):
        return "MILITARY"

    if "электив" in subject.casefold():
        return "ELECTIVE"

    return "REGULAR"


def _build_identity_key(
    subject: str,
    start_time: datetime,
    category: str,
) -> str:
    """
    Создаёт внутреннюю идентичность занятия.

    ВАЖНО:

    UID недельного и семестрового ICS у одного занятия
    может отличаться.

    Поэтому:

        MAI UID != identity

    Identity строится из:

        дата
        локальное время начала
        предмет
        категория

    Преподаватель и аудитория сюда специально НЕ входят,
    потому что они могут измениться.
    """
    raw = "|".join(
        [
            start_time.date().isoformat(),
            start_time.strftime("%H:%M"),
            subject.strip().casefold(),
            category,
        ]
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:32]


def _serialize_component(component: Any) -> str:
    """
    Сохраняет исходный VEVENT для отладки.
    """
    return component.to_ical().decode(
        "utf-8",
        errors="replace",
    )


def parse_ics(
    content: bytes,
    *,
    include_military: bool = False,
) -> list[LessonData]:
    """
    Парсит ICS-файл МАИ.

    По умолчанию военная подготовка полностью исключается.

    Для пользователя без военной подготовки:

        parse_ics(data)

    Для пользователя, которому она нужна:

        parse_ics(data, include_military=True)
    """
    calendar = Calendar.from_ical(content)

    result: list[LessonData] = []

    for component in calendar.walk("VEVENT"):
        uid = _clean(
            _text(component.get("UID"))
        )

        subject = (
            _clean(
                _text(component.get("SUMMARY"))
            )
            or "Без названия"
        )

        description = _clean(
            _text(component.get("DESCRIPTION"))
        )

        room = _clean(
            _text(component.get("LOCATION"))
        )

        start_time = _parse_datetime(
            component.get("DTSTART")
        )

        end_time = _parse_datetime(
            component.get("DTEND")
        )

        if end_time <= start_time:
            raise ValueError(
                f"Invalid lesson interval: {subject!r}"
            )

        lesson_type, teachers = (
            _parse_description(
                description or ""
            )
        )

        category = _detect_category(
            subject,
            description or "",
        )

        # Для текущего профиля военная подготовка
        # вообще не должна попадать в систему.
        if (
            category == "MILITARY"
            and not include_military
        ):
            continue

        identity_key = _build_identity_key(
            subject,
            start_time,
            category,
        )

        result.append(
            LessonData(
                source_uid=uid,
                identity_key=identity_key,

                subject=subject,
                lesson_type=lesson_type,
                category=category,

                start_time=start_time,
                end_time=end_time,

                teacher=(
                    teachers[0]
                    if teachers
                    else None
                ),
                teachers=teachers,

                room=room,
                description=description,

                raw_ics=_serialize_component(
                    component
                ),
            )
        )

    return sorted(
        result,
        key=lambda lesson: lesson.start_time,
    )