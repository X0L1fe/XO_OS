from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TelegramLinkResponse(BaseModel):
    linked: bool
    code: str
    expires_at: datetime


class TelegramStatusResponse(BaseModel):
    linked: bool
    telegram_id: int | None = None
    linked_at: datetime | None = None


class TelegramUnlinkResponse(BaseModel):
    success: bool