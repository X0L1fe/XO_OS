from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import List, Optional

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
    hashed_password: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        nullable=False,
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    google_calendar_connections: Mapped[List["GoogleCalendarConnection"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    google_calendar_events: Mapped[List["GoogleCalendarEvent"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    lessons: Mapped[List["Lesson"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    focus_sessions: Mapped[List["FocusSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    focus_evidences: Mapped[List["FocusEvidence"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    gamification_xp: Mapped[List["GamificationXP"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    gamification_levels: Mapped[List["GamificationLevel"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    xp_transactions: Mapped[List["XPTransaction"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_stats: Mapped[Optional["UserStats"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    telegram_link_codes: Mapped[List["TelegramLinkCode"]] = relationship(
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
    connection_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    access_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    refresh_token: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    sync_token: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="google_calendar_connections")
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
    summary: Mapped[Optional[str]] = mapped_column(
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
    created_at_google: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    updated_at_google: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    recurring_event_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    original_start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    i_cal_uid: Mapped[Optional[str]] = mapped_column(
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

    # Relationships
    user: Mapped["User"] = relationship(back_populates="google_calendar_events")
    connection: Mapped["GoogleCalendarConnection"] = relationship(
        back_populates="google_calendar_events"
    )


class Lesson(Base):
    __tablename__ = "lessons"

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
    subject: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    lesson_type: Mapped[Optional[str]] = mapped_column(
        String(50),
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
    google_event_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_synced_content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    content_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    is_recurring: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    recurrence_exceptions: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="lessons")
    focus_sessions: Mapped[List["FocusSession"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
    )


class FocusSession(Base):
    __tablename__ = "focus_sessions"

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
    lesson_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("lessons.id"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_completed: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
    )
    xp_earned: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="focus_sessions")
    lesson: Mapped["Lesson"] = relationship(back_populates="focus_sessions")
    evidences: Mapped[List["FocusEvidence"]] = relationship(
        back_populates="focus_session",
        cascade="all, delete-orphan",
    )


class FocusEvidence(Base):
    __tablename__ = "focus_evidences"

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
    focus_session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("focus_sessions.id"),
        nullable=False,
        index=True,
    )
    evidence_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    evidence_data: Mapped[Optional[Text]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="focus_evidences")
    focus_session: Mapped["FocusSession"] = relationship(
        back_populates="evidences"
    )


class GamificationXP(Base):
    __tablename__ = "gamification_xp"

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
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    source: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="gamification_xp")


class GamificationLevel(Base):
    __tablename__ = "gamification_levels"

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
    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    xp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="gamification_levels")


class XPTransaction(Base):
    __tablename__ = "xp_transactions"

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
    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="xp_transactions")


class UserStats(Base):
    __tablename__ = "user_stats"

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
    total_focus_time: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    total_sessions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    completed_sessions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    average_session_length: Mapped[Optional[float]] = mapped_column(
        nullable=True,
    )
    longest_session: Mapped[Optional[int]] = mapped_column(
        nullable=True,
    )
    current_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    longest_streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_stats")


class TelegramLinkCode(Base):
    __tablename__ = "telegram_link_codes"

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
    code: Mapped[str] = mapped_column(
        String(32),
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
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="telegram_link_codes")


class LessonData:
    """
    This is a data transfer object for lesson data used in synchronization.
    It is not a database model.
    """

    def __init__(
        self,
        subject: Optional[str] = None,
        lesson_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        google_event_id: Optional[str] = None,
        content_hash: Optional[str] = None,
        is_recurring: bool = False,
        recurrence_rule: Optional[str] = None,
        recurrence_exceptions: Optional[str] = None,
    ):
        self.subject = subject
        self.lesson_type = lesson_type
        self.start_time = start_time
        self.end_time = end_time
        self.google_event_id = google_event_id
        self.content_hash = content_hash
        self.is_recurring = is_recurring
        self.recurrence_rule = recurrence_rule
        self.recurrence_exceptions = recurrence_exceptions