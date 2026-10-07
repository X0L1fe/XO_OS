from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from app.auth.service import get_current_active_user
from app.database.models import User
from app.event import event_publisher

router = APIRouter()


@router.get("/events")
async def events_endpoint(
    request: Request,
    current_user: User = Depends(get_current_active_user),
):
    """
    Server-Sent Events endpoint for real-time updates.
    """
    return StreamingResponse(
        event_publisher(current_user.id),
        media_type="text/event-stream",
    )