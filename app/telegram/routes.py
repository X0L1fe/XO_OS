from __future__ import annotations

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from app.telegram_bot import telegram_bot_app
from app.auth.service import get_current_active_user
from app.database.models import User
from app.telegram.service import create_telegram_link_code, unlink_telegram_account
from app.telegram.schemas import (
    TelegramLinkResponse,
    TelegramStatusResponse,
    TelegramUnlinkResponse,
)
from app.database.db import Database
from app.config import Settings

db = Database()
settings = Settings()

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhook/telegram")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    """
    Handle incoming webhooks from Telegram.
    """
    try:
        data = await request.json()
        # Process the update in the background
        background_tasks.add_task(telegram_bot_app.process_update, data)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return {"status": "error"}


@router.post(
    "/telegram/link",
    response_model=TelegramLinkResponse,
)
async def telegram_link(
    current_user: User = Depends(get_current_active_user),
) -> TelegramLinkResponse:
    """
    Создаёт одноразовый код привязки учетной записи Telegram
    и создаёт Telegram deep link (/start CODE).
    """

    with db.session() as db_session:
        code, expires_at = create_telegram_link_code(
            db_session,
            current_user.id,
        )

    bot_username = settings.telegram_bot_username.strip().lstrip("@")

    if not bot_username:
        raise HTTPException(
            status_code=500,
            detail="Telegram bot username is not configured",
        )

    deep_link = f"https://t.me/{bot_username}?start={code}"

    return TelegramLinkResponse(
        linked=False,
        code=code,
        expires_at=expires_at,
        deep_link=deep_link,
    )


@router.get(
    "/telegram/status",
    response_model=TelegramStatusResponse,
)
async def telegram_status(
    current_user: User = Depends(get_current_active_user),
) -> TelegramStatusResponse:
    """
    Return Telegram connection status.
    """

    return TelegramStatusResponse(
        linked=current_user.telegram_id is not None,
        telegram_id=current_user.telegram_id,
        linked_at=current_user.telegram_linked_at,
    )


@router.post(
    "/telegram/unlink",
    response_model=TelegramUnlinkResponse,
)
async def telegram_unlink(
    current_user: User = Depends(get_current_active_user),
) -> TelegramUnlinkResponse:
    """
    Unlink Telegram account.
    """

    with db.session() as db_session:
        unlink_telegram_account(
            db_session,
            current_user.id,
        )

    return TelegramUnlinkResponse(
        success=True,
    )