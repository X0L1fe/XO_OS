from __future__ import annotations

import hashlib
import json
from datetime import datetime, time, timezone
from typing import List, Optional

import httpx

from app.ics.parser import LessonData


def _parse_time(t_str: str) -> time:
    # t_str format: "HH:MM:SS"
    return datetime.strptime(t_str, "%H:%M:%S").time()


def _parse_date(d_str: str) -> datetime.date:
    # d_str format: "DD.MM.YYYY"
    return datetime.strptime(d_str, "%d.%m.%Y").date()


def _build_identity_key(
    subject: str, date_str: str, time_start: str, time_end: str, teacher: str, room: str
) -> str:
    raw = f"{subject}|{date_str}|{time_start}|{time_end}|{teacher}|{room}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def parse_mais_schedule(
    json_content: bytes, group_name: Optional[str] = None
) -> List[LessonData]:
    """
    Parse MAIS schedule JSON into list of LessonData.
    If group_name is provided, verify that the JSON's group field matches.
    """
    from zoneinfo import ZoneInfo

    MAI_TIMEZONE = ZoneInfo("Europe/Moscow")

    def _parse_time(t_str: str) -> time:
        # t_str format: "HH:MM:SS"
        return datetime.strptime(t_str, "%H:%M:%S").time()

    def _parse_date(d_str: str) -> datetime.date:
        # d_str format: "DD.MM.YYYY"
        return datetime.strptime(d_str, "%d.%m.%Y").date()

    data = json.loads(json_content.decode("utf-8"))
    if group_name is not None:
        if data.get("group") != group_name:
            raise ValueError(
                f"Group mismatch: expected {group_name}, got {data.get('group')}"
            )
    # Ensure group field exists
    group = data.get("group", "")
    lessons: List[LessonData] = []

    # Mapping from MAIS type abbreviations to our lesson_type strings
    type_mapping = {
        "ЛК": "LECTURE",
        "ПЗ": "PRACTICE",
        "ЛБ": "LAB",
        "ЭК": "EXAM",
    }

    for date_str, day_info in data.items():
        if date_str == "group":
            continue
        # day_info is dict with keys "day" and "pairs"
        if not isinstance(day_info, dict):
            continue
        # day_name = day_info.get("day", "")  # not needed for identity
        pairs = day_info.get("pairs", {})
        if not isinstance(pairs, dict):
            continue
        for time_start_str, pair_dict in pairs.items():
            if not isinstance(pair_dict, dict):
                continue
            # pair_dict maps subject name to lesson details
            for subject, lesson_info in pair_dict.items():
                if not isinstance(lesson_info, dict):
                    continue
                time_start = lesson_info.get("time_start")
                time_end = lesson_info.get("time_end")
                lector_dict = lesson_info.get("lector", {})
                room_dict = lesson_info.get("room", {})
                type_dict = lesson_info.get("type", {})
                # lms, teams, other ignored for now

                # Extract teacher (first non-empty value) and collect all teachers
                teacher_list = []
                if lector_dict:
                    # lector_dict maps UUID to FIO string
                    for v in lector_dict.values():
                        if isinstance(v, str) and v.strip():
                            teacher_list.append(v.strip())
                teacher = teacher_list[0] if teacher_list else None

                # Extract room (first non-empty value)
                room = ""
                if room_dict:
                    for v in room_dict.values():
                        if isinstance(v, str) and v.strip():
                            room = v.strip()
                            break

                # Determine lesson type
                lesson_type = "OTHER"
                if isinstance(type_dict, dict):
                    for abbr in type_dict.keys():
                        if abbr in type_mapping:
                            lesson_type = type_mapping[abbr]
                            break

                # Skip if essential fields missing
                if not time_start or not time_end:
                    continue
                try:
                    start_time_obj = _parse_time(time_start)
                    end_time_obj = _parse_time(time_end)
                except ValueError:
                    continue
                date_obj = _parse_date(date_str)
                start_dt_naive = datetime.combine(date_obj, start_time_obj)
                end_dt_naive = datetime.combine(date_obj, end_time_obj)
                start_dt = start_dt_naive.replace(tzinfo=MAI_TIMEZONE)
                end_dt = end_dt_naive.replace(tzinfo=MAI_TIMEZONE)

                # Build identity key based on date, time, subject, and category (REGULAR)
                # This matches the approach in ics/parser.py's _build_identity_key
                raw = "|".join(
                    [
                        start_dt.date().isoformat(),
                        start_dt.strftime("%H:%M"),
                        subject.strip().casefold(),
                        "REGULAR",  # MAIS data doesn't specify category, assume regular
                    ]
                )
                identity_key = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

                # Prepare description: include room and teacher for display in Google Calendar
                description_parts = []
                if room:
                    description_parts.append(f"Аудитория: {room}")
                if teacher:
                    description_parts.append(f"Преподаватель: {teacher}")
                description = (
                    "\n".join(description_parts) if description_parts else None
                )

                lesson = LessonData(
                    source_uid="",  # MAIS JSON doesn't provide a UID
                    identity_key=identity_key,
                    subject=subject or "",
                    lesson_type=lesson_type,
                    category="REGULAR",
                    start_time=start_dt,
                    end_time=end_dt,
                    teacher=teacher,
                    teachers=tuple(teacher_list),
                    room=room if room else None,
                    description=description,
                    raw_ics="",  # Not applicable for MAIS JSON
                )
                lessons.append(lesson)
    return lessons


def fetch_groups() -> List[dict]:
    """
    Fetch the list of groups from MAIS.
    Returns list of dict with keys: name, fac, level, course.
    """
    import urllib.request

    req = urllib.request.Request(
        "https://public.mai.ru/schedule/data/groups.json",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def fetch_group_schedule(group_name: str) -> bytes:
    """
    Fetch schedule JSON for a given group name.
    Uses MD5 of group name as the filename.
    """
    import hashlib
    import urllib.request

    md5_hash = hashlib.md5(group_name.encode("utf-8")).hexdigest()
    url = f"https://public.mai.ru/schedule/data/{md5_hash}.json"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read()


# Trigger reload


async def async_fetch_groups() -> List[dict]:
    """
    Fetch the list of groups from MAIS asynchronously.
    Returns list of dict with keys: name, fac, level, course.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://public.mai.ru/schedule/data/groups.json",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        return response.json()


async def async_fetch_group_schedule(group_name: str) -> bytes:
    """
    Fetch schedule JSON for a given group name asynchronously.
    Uses MD5 of group name as the filename.
    """
    md5_hash = hashlib.md5(group_name.encode("utf-8")).hexdigest()
    url = f"https://public.mai.ru/schedule/data/{md5_hash}.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        return response.content
