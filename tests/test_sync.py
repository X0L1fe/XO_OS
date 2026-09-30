from pathlib import Path

from sqlalchemy import select

from app.database.db import Database
from app.database.models import Lesson, User
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

    # Create a test user
    with db.session() as session:
        user = User(
            email="test@example.com",
            name="Test User",
            password_hash="hashed_password",
            is_active=1,
            onboarding_completed=1,
            email_verified=1,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    first = service.import_ics(ICS_V1, user_id=user_id)

    assert first.created == 1
    assert first.updated == 0
    assert first.moved == 0
    assert first.deleted == 0

    second = service.import_ics(ICS_V2, user_id=user_id)

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
