from pathlib import Path

from sqlalchemy import select

from app.database.db import Database
from app.database.models import Lesson
from app.sync.service import SyncService


ICS_V1 = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test-1
DTSTART:20260905T100000Z
DTEND:20260905T113000Z
SUMMARY:Теория графов
DESCRIPTION:ЛК: ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА
LOCATION:ГУК В-214
END:VEVENT
END:VCALENDAR
""".encode("utf-8")

ICS_V2 = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
UID:test-1
DTSTART:20260905T104500Z
DTEND:20260905T121500Z
SUMMARY:Теория графов
DESCRIPTION:ПЗ: ЕГОРОВА ЕВГЕНИЯ КИРИЛЛОВНА
LOCATION:ГУК В-214
END:VEVENT
BEGIN:VEVENT
UID:test-2
DTSTART:20260906T090000Z
DTEND:20260906T103000Z
SUMMARY:Программирование
DESCRIPTION:ЛК: Петров П.П.
LOCATION:301
END:VEVENT
END:VCALENDAR
""".encode("utf-8")


def test_create_update_and_delete(tmp_path: Path):
    db = Database(f"sqlite:///{tmp_path / 'test.db'}")
    service = SyncService(db)

    first = service.import_ics(ICS_V1)

    assert first.created == 1
    assert first.updated == 0
    assert first.moved == 0
    assert first.deleted == 0

    second = service.import_ics(ICS_V2)

    # Теория графов:
    #
    # 10:00 → 10:45
    #
    # Это существующее занятие,
    # которое было перенесено.
    assert second.moved == 1

    # Программирование появилось впервые.
    assert second.created == 1

    assert second.updated == 0
    assert second.deleted == 0
