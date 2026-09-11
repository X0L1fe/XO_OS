
from __future__ import annotations

from datetime import datetime, timezone, timedelta

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
        )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
        )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
        )
    password_hash: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
        )
    is_active: Mapped[bool] = mapped_column(
        Integer, 
        default=1
        )  # using Integer for boolean compatibility with SQLite
    onboarding_completed: Mapped[bool] = mapped_column(
        Integer, 
        default=0
        )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
        )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
        )

    # Relationship to UserStats (one-to-one)
    stats: Mapped['UserStats'] = relationship(
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
        )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
        index=True,
    )
    telegram_linked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

class TelegramLinkCode(Base):
    __tablename__ = "telegram_link_codes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    code_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    used: Mapped[bool] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship()

class UserStats(Base):
    __tablename__ = 'user_stats'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
        )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        unique=True,
        nullable=False
        )
    total_xp: Mapped[int] = mapped_column(
        Integer,
        default=0
        )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0
        )
    max_streak: Mapped[int] = mapped_column(
        Integer,
        default=0
        )
    last_activity_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
        )
    level: Mapped[int] = mapped_column(
        Integer, 
        default=1
        )

    # Relationship to User
    user: Mapped['User'] = relationship(back_populates='stats')


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True
        )
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False
        )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
        )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
        )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
        )

    # Relationship to User
    user: Mapped['User'] = relationship()


class Lesson(Base):
    __tablename__ = 'lessons'

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
        )
    stable_id: Mapped[str] = mapped_column(
        String(128), 
        index=True
        )
    source_uid: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
        )
    subject: Mapped[str] = mapped_column(
        String(255)
        )
    lesson_type: Mapped[str] = mapped_column(
        String(32), 
        default='OTHER'
        )
    category: Mapped[str] = mapped_column(
        String(32),
        default='REGULAR'
        )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True
        )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
        )
    teacher: Mapped[str | None] = mapped_column(
        String(255), 
        nullable=True
        )
    room: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
        )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
        )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True
        )
    google_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True
        )
    last_synced_content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True
        )
    raw_ics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
        )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc)
        )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc)
        )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
        )
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'),
        nullable=False,
        index=True
        )
    user: Mapped['User'] = relationship()

