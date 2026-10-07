from __future__ import annotations

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import RedirectResponse
from typing import Optional
import os

from app.auth.service import get_current_active_user, get_current_user
from app.config import Settings
from app.database.db import Database
db = Database()
from app.config import Settings
settings = Settings()

# Try to import Google Calendar service; if not available, set to None.
try:
    from google_auth_oauthlib.flow import Flow
    from app.google_calendar.auth import (
        SCOPES,
        get_credentials_path,
        get_google_calendar_service,
        get_token_path,
    )
    from app.google_calendar.service import GoogleCalendarSyncService

    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GoogleCalendarSyncService = None
    get_google_calendar_service = None
    GOOGLE_OAUTH_AVAILABLE = False

router = APIRouter(
    prefix="/google",
    tags=["google_calendar"],
)


@router.get("/auth")
async def google_auth():
    """Initiate Google OAuth2 flow."""
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth not available",
        )
    try:
        flow = Flow.from_client_secrets_file(
            get_credentials_path(),
            scopes=SCOPES,
            redirect_uri="http://127.0.0.1:8000/api/google/callback",
        )
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        response = RedirectResponse(url=authorization_url)
        response.set_cookie(
            key="oauth_state",
            value=state,
            httponly=True,
            max_age=600,
            samesite="lax",
        )
        response.set_cookie(
            key="oauth_code_verifier",
            value=flow.code_verifier,
            httponly=True,
            max_age=600,
            samesite="lax",
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate OAuth flow: {e}",
        )


@router.get("/callback")
async def google_callback(request: Request):
    """Handle Google OAuth2 callback."""
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Google OAuth not available",
        )
    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        saved_state = request.cookies.get("oauth_state")
        code_verifier = request.cookies.get("oauth_code_verifier")
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Missing authorization code",
            )
        if not state or state != saved_state:
            raise HTTPException(
                status_code=400,
                detail="Invalid OAuth state",
            )
        if not code_verifier:
            raise HTTPException(
                status_code=400,
                detail="Missing PKCE code verifier",
            )
        flow = Flow.from_client_secrets_file(
            get_credentials_path(),
            scopes=SCOPES,
            redirect_uri="http://127.0.0.1:8000/api/google/callback",
            code_verifier=code_verifier,
            autogenerate_code_verifier=False,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(
            get_token_path(),
            "w",
            encoding="utf-8",
        ) as token_file:
            token_file.write(creds.to_json())
        response = RedirectResponse(
            url="http://127.0.0.1:8000/#settings?connected=true"
        )
        response.delete_cookie("oauth_state")
        response.delete_cookie("oauth_code_verifier")
        return response
    except Exception as e:
        return RedirectResponse(url=(f"http://127.0.0.1:8000/#settings?error={str(e)}"))


@router.get("/status")
async def google_status(current_user: User = Depends(get_current_user)):
    """Check Google connection status and last sync time."""
    if not GOOGLE_OAUTH_AVAILABLE:
        return {"connected": False, "error": "Google OAuth not available"}
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.valid:
                return {
                    "connected": True,
                    "last_synced_at": current_user.last_synced_at.isoformat()
                    if current_user.last_synced_at
                    else None,
                }
            elif creds and creds.expired and creds.refresh_token:
                # Try to refresh
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, "w") as token_file:
                    token_file.write(creds.to_json())
                return {
                    "connected": True,
                    "last_synced_at": current_user.last_synced_at.isoformat()
                    if current_user.last_synced_at
                    else None,
                }
        return {"connected": False, "last_synced_at": None}
    except Exception:
        return {"connected": False, "last_synced_at": None}


@router.post("/disconnect")
async def google_disconnect():
    """Disconnect/revoke Google OAuth tokens."""
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(status_code=501, detail="Google OAuth not available")
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            os.remove(token_path)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")


@router.get("/calendars")
async def get_google_calendars(current_user: User = Depends(get_current_active_user)):
    """Get list of user's Google Calendars."""
    if not GOOGLE_OAUTH_AVAILABLE or get_google_calendar_service is None:
        # Return default primary calendar if Google OAuth is not available
        return {
            "calendars": [{"id": "primary", "summary": "Основной календарь"}],
            "requires_auth": False,
        }
    try:
        # Check if user has Google credentials
        token_path = get_token_path()
        if not os.path.exists(token_path):
            # No token file, user not authenticated with Google
            return {
                "calendars": [{"id": "primary", "summary": "Основной календарь"}],
                "requires_auth": True,
            }

        # Try to get the service
        service = get_google_calendar_service()
        calendar_list = service.calendarList().list().execute()
        calendars = []
        for calendar in calendar_list.get("items", []):
            calendars.append(
                {
                    "id": calendar["id"],
                    "summary": calendar.get("summary", "Без названия"),
                }
            )
        # Always include primary calendar as fallback
        if not any(cal["id"] == "primary" for cal in calendars):
            calendars.append({"id": "primary", "summary": "Основной календарь"})
        return {"calendars": calendars, "requires_auth": False}
    except Exception as e:
        # If there's an error (e.g., not authenticated), return default with auth required
        return {
            "calendars": [{"id": "primary", "summary": "Основной календарь"}],
            "requires_auth": True,
        }


@router.post("/calendar/select")
async def select_google_calendar(
    request: Request, current_user: User = Depends(get_current_active_user)
):
    """Save the user's selected Google Calendar ID for synchronization."""
    try:
        data = await request.json()
        calendar_id = data.get("calendar_id")

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()
            user.selected_calendar_id = calendar_id if calendar_id else None
            session.commit()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save calendar selection: {str(e)}"
        )