from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database.models import Base

DB_PATH = Path("data")
DB_PATH.mkdir(exist_ok=True)


class Database:
    def __init__(self, url: str | None = None) -> None:
        self.url = url or settings.database_url
        connect_args = (
            {"check_same_thread": False} if self.url.startswith("sqlite") else {}
        )
        self.engine = create_engine(self.url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def session(self):
        return self.SessionLocal()


db = Database()
