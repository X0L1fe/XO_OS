from __future__ import annotations

import hashlib
import secrets
import string
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session as SQLAlchemySession

from app.database.models import TelegramLinkCode, User


LINK_CODE_TTL = timedelta(minutes=10)

# Только легко читаемые символы.
# Исключаем O/0 и I/1, чтобы не было путаницы.
CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 10


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _make_code() -> str:
    return "".join(
        secrets.choice(CODE_ALPHABET)
        for _ in range(CODE_LENGTH)
    )


def _hash_code(code: str) -> str:
    return hashlib.sha256(
        code.strip().upper().encode("utf-8")
    ).hexdigest()


def _normalize_datetime(value: datetime) -> datetime:
    """
    SQLite может вернуть datetime без tzinfo даже при
    DateTime(timezone=True). В нашем проекте такие значения
    считаем UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def create_telegram_link_code(
    db: SQLAlchemySession,
    user_id: int,
) -> tuple[str, datetime]:
    """
    Создаёт новый одноразовый код привязки Telegram.

    Старые активные коды этого пользователя удаляются.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user.telegram_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Telegram уже привязан",
        )

    # Удаляем старые неиспользованные коды.
    db.query(TelegramLinkCode).filter(
        TelegramLinkCode.user_id == user_id,
        TelegramLinkCode.used == False,
    ).delete(
        synchronize_session=False,
    )

    code = _make_code()
    code_hash = _hash_code(code)

    expires_at = _utc_now() + LINK_CODE_TTL

    link_code = TelegramLinkCode(
        user_id=user_id,
        code_hash=code_hash,
        expires_at=expires_at,
        used=False,
    )

    db.add(link_code)
    db.commit()

    return code, expires_at


def link_telegram_account(
    db: SQLAlchemySession,
    code: str,
    telegram_id: int,
) -> User:
    """
    Проверяет одноразовый код и привязывает telegram_id
    к пользователю.
    """

    normalized_code = code.strip().upper()

    if not normalized_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пустой код",
        )

    code_hash = _hash_code(normalized_code)

    link_code = (
        db.query(TelegramLinkCode)
        .filter(
            TelegramLinkCode.code_hash == code_hash,
            TelegramLinkCode.used == False,
        )
        .first()
    )

    if not link_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код недействителен или уже использован",
        )

    expires_at = _normalize_datetime(link_code.expires_at)

    if expires_at <= _utc_now():
        link_code.used = True
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия кода истёк",
        )

    user = (
        db.query(User)
        .filter(User.id == link_code.user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    # Проверяем, не привязан ли этот Telegram
    # к другому аккаунту.
    existing_user = (
        db.query(User)
        .filter(
            User.telegram_id == telegram_id,
            User.id != user.id,
        )
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот Telegram уже привязан к другому аккаунту XO_OS",
        )

    user.telegram_id = telegram_id
    user.telegram_linked_at = _utc_now()

    link_code.used = True

    # Удаляем остальные активные коды пользователя.
    db.query(TelegramLinkCode).filter(
        TelegramLinkCode.user_id == user.id,
        TelegramLinkCode.id != link_code.id,
        TelegramLinkCode.used == False,
    ).delete(
        synchronize_session=False,
    )

    db.commit()
    db.refresh(user)

    return user


def get_user_by_telegram_id(
    db: SQLAlchemySession,
    telegram_id: int,
) -> User | None:
    """
    Возвращает пользователя, связанного с Telegram ID.
    """

    return (
        db.query(User)
        .filter(User.telegram_id == telegram_id)
        .first()
    )


def unlink_telegram_account(
    db: SQLAlchemySession,
    user_id: int,
) -> None:
    """
    Отвязывает Telegram от пользователя.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    user.telegram_id = None
    user.telegram_linked_at = None

    db.query(TelegramLinkCode).filter(
        TelegramLinkCode.user_id == user_id,
    ).delete(
        synchronize_session=False,
    )

    db.commit()