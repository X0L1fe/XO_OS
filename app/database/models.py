from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Integer,
        default=1,
    )  # using Integer for boolean compatibility with SQLite
    onboarding_completed: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )
    email_verified: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )  # Track if email has been verified
    verification_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )  # Hashed verification token for email verification
    verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )  # Expiration time for verification token
    # Fields for email change
    email_change_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )  # Hashed token for email change verification
    email_change_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )  # Expiration for email change token
    new_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )  # Pending new email address
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationship to UserStats (one-to-one)
    stats: Mapped["UserStats"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
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
    # MAIS group ID (the group name or identifier from MAIS API)
    mais_group_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # Selected Google Calendar ID for synchronization
    selected_calendar_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # Whether notifications for schedule changes are enabled
    notifications_enabled: Mapped[bool] = mapped_column(
        Integer,
        default=1,
    )  # using Integer for boolean compatibility with SQLite
    # Last time we checked for MAIS schedule changes
    last_mais_check: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # List of notifications for this user
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")
    # Last time we successfully synchronized with Google Calendar
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # AI verification enabled setting
    ai_verification_enabled: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )  # using Integer for boolean compatibility with SQLite
    schedule_exclusions: Mapped[List["ScheduleExclusion"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
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
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    total_xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    max_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    last_activity_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    # Relationship to User
    user: Mapped["User"] = relationship(back_populates="stats")


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    # Relationship to User
    user: Mapped["User"] = relationship()


class Notification(Base):
    __tablename__ = "notifications"

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
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_read: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )  # using Integer for boolean compatibility with SQLite
    type: Mapped[str] = mapped_column(
        String(50),
        default="info",
    )  # e.g., "schedule_change", "system", "reminder"
    related_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )  # ID of related entity (e.g., lesson ID)
    related_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )  # Type of related entity (e.g., "lesson")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    # Relationship to User
    user: Mapped["User"] = relationship(back_populates="notifications")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    stable_id: Mapped[str] = mapped_column(
        String(128),
        index=True,
    )
    source_uid: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    subject: Mapped[str] = mapped_column(
        String(255),
    )
    lesson_type: Mapped[str] = mapped_column(
        String(32),
        default="OTHER",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        default="REGULAR",
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    teacher: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    room: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )
    google_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
    )
    last_synced_content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    raw_ics: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # MAIS group ID (the group name or identifier from MAIS API) for this lesson
    mais_group_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    # Foreign key to User
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship()


class ScheduleExclusion(Base):
    """
    Исключение из отображения расписания пользователя.

    exclusion_type:
        - "category" — исключить категорию
        - "subject"  — исключить предмет

    value_key:
        Нормализованное значение, по которому выполняется сравнение.

    value_label:
        Человекочитаемое значение для интерфейса.
    """

    __tablename__ = "schedule_exclusions"

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

    exclusion_type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )

    value_key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    value_label: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        back_populates="schedule_exclusions",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "exclusion_type",
            "value_key",
            name="uq_schedule_exclusion_user_type_key",
        ),
    )


class FocusSession(Base):
    __tablename__ = "focus_sessions"

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
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id"),
        nullable=True,
        index=True,
    )
    goal_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(timezone.utc),
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    paused_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    total_paused_seconds: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )  # active, paused, completed, cancelled
    completion_mode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )  # manual, ai_verified
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_required",
    )  # not_required, pending, approved, partial, rejected, error
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0)
    evidence_provided: Mapped[bool] = mapped_column(Integer, default=0)  # using Integer for boolean compatibility with SQLite
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    user: Mapped["User"] = relationship()
    lesson: Mapped["Lesson"] = relationship()


class FocusEvidence(Base):
    __tablename__ = "focus_evidence"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    focus_session_id: Mapped[int] = mapped_column(
        ForeignKey("focus_sessions.id"),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # text, url, image, file
    content: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    # Relationship
    focus_session: Mapped["FocusSession"] = relationship()


class XPTransaction(Base):
    __tablename__ = "xp_transactions"

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
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    # Relationship
    user: Mapped["User"] = relationship()