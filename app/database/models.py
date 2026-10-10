from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import (
    JSON,
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
    )
    onboarding_completed: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )
    email_verified: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )
    verification_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    email_change_token_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        index=True,
    )
    email_change_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    new_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

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
    mais_group_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    selected_calendar_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Integer,
        default=1,
    )
    last_mais_check: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ai_verification_enabled: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )
    lesson_colors: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )
    custom_colors: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user",
    )
    schedule_exclusions: Mapped[List["ScheduleExclusion"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    google_calendar_connections: Mapped[List["GoogleCalendarConnection"]] = (
        relationship(
            back_populates="user",
            cascade="all, delete-orphan",
        )
    )
    google_calendar_events: Mapped[List["GoogleCalendarEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class GoogleCalendarConnection(Base):
    __tablename__ = "google_calendar_connections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    calendar_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    connection_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    access_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    refresh_token: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False,
    )
    sync_token: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    enabled: Mapped[bool] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="google_calendar_connections",
    )
    google_calendar_events: Mapped[List["GoogleCalendarEvent"]] = relationship(
        back_populates="connection",
        cascade="all, delete-orphan",
    )


class GoogleCalendarEvent(Base):
    __tablename__ = "google_calendar_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    connection_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("google_calendar_connections.id"),
        nullable=False,
        index=True,
    )
    google_event_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    calendar_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    summary: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at_google: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at_google: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    recurring_event_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    original_start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    i_cal_uid: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    is_all_day: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "google_event_id",
            name="uq_connection_google_event_id",
        ),
    )

    user: Mapped["User"] = relationship(
        back_populates="google_calendar_events",
    )
    connection: Mapped["GoogleCalendarConnection"] = relationship(
        back_populates="google_calendar_events",
    )


class UserStats(Base):
    __tablename__ = "user_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
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
    last_activity_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    user: Mapped["User"] = relationship(
        back_populates="stats",
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
    )
    type: Mapped[str] = mapped_column(
        String(50),
        default="info",
    )
    related_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    related_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship(
        back_populates="notifications",
    )


class Lesson(Base):
    __tablename__ = "lessons"

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
    mais_group_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    last_color_value: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    user: Mapped["User"] = relationship()
    focus_sessions: Mapped[List["FocusSession"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )


class ScheduleExclusion(Base):
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
    goal_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
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
    total_paused_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )
    completion_mode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    verification_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_required",
    )
    verification_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    verification_missing: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    xp_awarded: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )
    evidence_provided: Mapped[bool] = mapped_column(
        Integer,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship()
    lesson: Mapped["Lesson"] = relationship(
        back_populates="focus_sessions",
    )


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
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    file_path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

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
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    source_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship()
