from __future__ import annotations

import hashlib
import json
from datetime import datetime, time, timezone
from typing import List, Optional

from app.ics.parser import LessonData


def _parse_time(t_str: str) -> time:
    # t_str format: "HH:MM:SS"
    return datetime.strptime(t_str, "%H:%M:%S").time()


def _parse_date(d_str: str) -> datetime.date:
    # d_str format: "DD.MM.YYYY"
    return datetime.strptime(d_str, "%d.%m.%Y").date()


def _build_identity_key(subject: str, date_str: str, time_start: str, time_end: str, teacher: str, room: str) -> str:
    raw = f"{subject}|{date_str}|{time_start}|{time_end}|{teacher}|{room}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def parse_mais_schedule(json_content: bytes, group_name: Optional[str] = None) -> List[LessonData]:
    """
    Parse MAIS schedule JSON into list of LessonData.
    If group_name is provided, verify that the JSON's group field matches.
    """
    data = json.loads(json_content.decode("utf-8"))
    if group_name is not None:
        if data.get("group") != group_name:
            raise ValueError(f"Group mismatch: expected {group_name}, got {data.get('group')}")
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
        day_name = day_info.get("day", "")
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

                # Extract teacher (first non-empty value)
                teacher = ""
                if lector_dict:
                    # lector_dict maps UUID to FIO string
                    for v in lector_dict.values():
                        if isinstance(v, str) and v.strip():
                            teacher = v.strip()
                            break
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
                    start_time = _parse_time(time_start)
                    end_time = _parse_time(time_end)
                except ValueError:
                    continue
                date_obj = _parse_date(date_str)
                start_dt = datetime.combine(date_obj, start_time, tzinfo=timezone.utc)
                end_dt = datetime.combine(date_obj, end_time, tzinfo=timezone.utc)

                identity_key = _build_identity_key(subject, date_str, time_start, time_end, teacher, room)

                lesson = LessonData(
                    identity_key=identity_key,
                    subject=subject or "",
                    lesson_type=lesson_type,
                    category="REGULAR",
                    start_time=start_dt,
                    end_time=end_dt,
                    teacher=teacher if teacher else None,
                    teachers=(teacher,) if teacher else (),
                    room=room if room else None,
                    description=None,
                    raw_ics="",
                    source_uid="",
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
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
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
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req) as resp:
        return resp.read()


# Trigger reload