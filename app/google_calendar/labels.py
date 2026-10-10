"""
Определения меток событий Google Calendar.

Особенности Google Calendar API:
- Каждая метка должна быть зарегистрирована в самом календаре
  через calendars().patch() с полем labelProperties.eventLabels.
- id метки должен быть в формате UUID.

Чтобы не хранить UUID в БД, генерируем их детерминированно
через uuid5(namespace, seed). Один и тот же seed всегда даёт
один и тот же UUID.
"""

from __future__ import annotations

import uuid

# Свой namespace, чтобы UUID не пересекались с чужими
_XO_OS_NAMESPACE = uuid.UUID("6f3b4c8a-1a2e-4f5b-9c7d-8e1f2a3b4c5d")


# ----------------------------------------------------------------
# 24 палитровых цвета
# ----------------------------------------------------------------

PALETTE_COLORS = [
    {"key": "cocoa", "name": "Какао", "hex": "#ac725e"},
    {"key": "flamingo", "name": "Фламинго", "hex": "#d06b64"},
    {"key": "tomato", "name": "Томат", "hex": "#f83a22"},
    {"key": "tangerine", "name": "Мандарин", "hex": "#fa573c"},
    {"key": "pumpkin", "name": "Тыква", "hex": "#ff7537"},
    {"key": "mango", "name": "Манго", "hex": "#ffad46"},
    {"key": "citron", "name": "Лимон", "hex": "#fad165"},
    {"key": "banana", "name": "Банан", "hex": "#fbe983"},
    {"key": "avocado", "name": "Авокадо", "hex": "#b3dc6c"},
    {"key": "pistachio", "name": "Фисташка", "hex": "#7bd148"},
    {"key": "basil", "name": "Базилик", "hex": "#16a765"},
    {"key": "eucalyptus", "name": "Эвкалипт", "hex": "#42d692"},
    {"key": "peacock", "name": "Павлин", "hex": "#9fe1e7"},
    {"key": "cobalt", "name": "Кобальт", "hex": "#9fc6e7"},
    {"key": "blueberry", "name": "Черника", "hex": "#4986e7"},
    {"key": "lavender", "name": "Лаванда", "hex": "#9a9cff"},
    {"key": "wisteria", "name": "Глициния", "hex": "#b99aff"},
    {"key": "amethyst", "name": "Аметист", "hex": "#cd74e6"},
    {"key": "grape", "name": "Виноград", "hex": "#a47ae2"},
    {"key": "cherry_blossom", "name": "Сакура", "hex": "#f691b2"},
    {"key": "beetroot", "name": "Свекла", "hex": "#cca6ac"},
    {"key": "radicchio", "name": "Радиччио", "hex": "#cabdbf"},
    {"key": "graphite", "name": "Графит", "hex": "#c2c2c2"},
    {"key": "birch", "name": "Береза", "hex": "#92e1c0"},
]


# ----------------------------------------------------------------
# 6 кастомных слотов
# ----------------------------------------------------------------

CUSTOM_SLOT_KEYS = [
    "custom_1",
    "custom_2",
    "custom_3",
    "custom_4",
    "custom_5",
    "custom_6",
]


# ----------------------------------------------------------------
# Генерация UUID
# ----------------------------------------------------------------


def palette_label_uuid(key: str) -> str:
    """
    UUID палитровой метки по её ключу (cocoa, mango, ...).
    """
    return str(uuid.uuid5(_XO_OS_NAMESPACE, f"palette.{key}"))


def custom_label_uuid(slot: str) -> str:
    """
    UUID кастомного слота (custom_1 .. custom_6).
    """
    if slot not in CUSTOM_SLOT_KEYS:
        raise ValueError(f"Unknown custom slot: {slot!r}")
    return str(uuid.uuid5(_XO_OS_NAMESPACE, f"custom.{slot}"))


def custom_label_name(slot: str) -> str:
    """
    Человекочитаемое имя кастомного слота, если пользователь не задал своё.
    """
    return f"Мой цвет {slot.split('_')[1]}"


# ----------------------------------------------------------------
# Разрешение значения из User.lesson_colors в eventLabelId
# ----------------------------------------------------------------


def resolve_event_label_id(value: str | int | None) -> tuple[str, str] | None:
    """
    Преобразует значение из lesson_colors в (тип_поля, значение) для Google API.

    Возвращает:
        ("colorId", "5")          — для legacy numeric colorId
        ("eventLabelId", "uuid")  — для метки
        None                      — если значение не распознано

    Поддерживает:
        - int / numeric string 1..11 → legacy colorId
        - "xo_os_<key>"              → палитровая метка
        - "custom_<n>"               → кастомная метка
        - "#rrggbb"                  → устаревший формат, маппится на custom_1
                                       (для обратной совместимости)
    """
    if value is None:
        return None

    if isinstance(value, int) and 1 <= value <= 11:
        return ("colorId", str(value))

    if isinstance(value, str):
        # legacy numeric colorId в виде строки
        if value.isdigit():
            n = int(value)
            if 1 <= n <= 11:
                return ("colorId", str(n))

        # палитровая метка
        if value.startswith("xo_os_"):
            key = value[len("xo_os_") :]
            try:
                return ("eventLabelId", palette_label_uuid(key))
            except Exception:
                return None

        # кастомный слот
        if value in CUSTOM_SLOT_KEYS:
            return ("eventLabelId", custom_label_uuid(value))

        # старый формат hex — не поддерживаем в новом API
        if value.startswith("#"):
            return None

    return None


# ----------------------------------------------------------------
# Полный список меток для регистрации в календаре
# ----------------------------------------------------------------


def build_all_labels(custom_colors: dict | None = None) -> list[dict]:
    """
    Возвращает список меток для передачи в calendars().patch().

    custom_colors — словарь вида:
        {"custom_1": {"hex": "#ff00ff", "name": "Розовый"}, ...}
    """
    labels: list[dict] = []

    # 24 палитровых
    for color in PALETTE_COLORS:
        labels.append(
            {
                "id": palette_label_uuid(color["key"]),
                "name": color["name"],
                "backgroundColor": color["hex"],
            }
        )

    # 6 кастомных (только те, что заданы пользователем)
    if custom_colors:
        for slot in CUSTOM_SLOT_KEYS:
            data = custom_colors.get(slot)
            if not data or not data.get("hex"):
                continue
            labels.append(
                {
                    "id": custom_label_uuid(slot),
                    "name": data.get("name") or custom_label_name(slot),
                    "backgroundColor": data["hex"],
                }
            )

    return labels
