from __future__ import annotations

from fastapi import APIRouter
import os

from app.google_calendar.routes import GOOGLE_OAUTH_AVAILABLE
from app.google_calendar.auth import (
    get_token_path,
    SCOPES,
)

router = APIRouter()


@router.get("/calendar/status")
def get_calendar_status():
    """Get calendar status."""
    if not GOOGLE_OAUTH_AVAILABLE:
        return {"status": "disconnected"}
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            from google.oauth2.credentials import Credentials

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.valid:
                return {"status": "connected"}
            elif creds and creds.expired and creds.refresh_token:
                # Try to refresh
                from google.auth.transport.requests import Request

                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())
                return {"status": "connected"}
        return {"status": "disconnected"}
    except Exception:
        return {"status": "disconnected"}