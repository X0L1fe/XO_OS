from __future__ import annotations

import logging
import os
import re as _re
from datetime import datetime, timezone
from typing import Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from fastapi.responses import RedirectResponse

from app.auth.service import get_current_active_user, get_current_user
from app.config import Settings
from app.database.db import Database
from app.google_calendar.labels import CUSTOM_SLOT_KEYS, PALETTE_COLORS

logger = logging.getLogger(__name__)
db = Database()
from app.config import Settings

settings = Settings()
from app.database.models import GoogleCalendarConnection, User

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


_HEX_RE = _re.compile(r"^#[0-9a-fA-F]{6}$")

ALLOWED_LESSON_TYPES = {"LECTURE", "PRACTICE", "LAB", "EXAM"}

ALLOWED_PALETTE_IDS = {
    "xo_os_cocoa",
    "xo_os_flamingo",
    "xo_os_tomato",
    "xo_os_tangerine",
    "xo_os_pumpkin",
    "xo_os_mango",
    "xo_os_citron",
    "xo_os_banana",
    "xo_os_avocado",
    "xo_os_pistachio",
    "xo_os_basil",
    "xo_os_eucalyptus",
    "xo_os_peacock",
    "xo_os_cobalt",
    "xo_os_blueberry",
    "xo_os_lavender",
    "xo_os_wisteria",
    "xo_os_amethyst",
    "xo_os_grape",
    "xo_os_cherry_blossom",
    "xo_os_beetroot",
    "xo_os_radicchio",
    "xo_os_graphite",
    "xo_os_birch",
}


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
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials

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
    # Всегда перечитываем пользователя из БД, чтобы получить актуальный selected_calendar_id
    with db.session() as session:
        user_db = session.query(User).filter(User.id == current_user.id).one()
        selected_calendar_id = user_db.selected_calendar_id

    if not GOOGLE_OAUTH_AVAILABLE or get_google_calendar_service is None:
        return {
            "calendars": [{"id": "primary", "summary": "Основной календарь"}],
            "selected_calendar_id": selected_calendar_id,
            "requires_auth": False,
        }

    try:
        token_path = get_token_path()
        if not os.path.exists(token_path):
            return {
                "calendars": [{"id": "primary", "summary": "Основной календарь"}],
                "selected_calendar_id": selected_calendar_id,
                "requires_auth": True,
            }

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
        if not any(cal["id"] == "primary" for cal in calendars):
            calendars.append({"id": "primary", "summary": "Основной календарь"})

        return {
            "calendars": calendars,
            "selected_calendar_id": selected_calendar_id,
            "requires_auth": False,
        }
    except Exception as e:
        return {
            "calendars": [{"id": "primary", "summary": "Основной календарь"}],
            "selected_calendar_id": selected_calendar_id,
            "requires_auth": True,
        }


@router.post("/calendar/select")
async def select_google_calendar(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """Save the user's selected Google Calendar ID for synchronization."""
    try:
        data = await request.json()
        calendar_id = data.get("calendar_id")

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()

            # If calendar_id is None or empty, treat as clearing selection (for backward compatibility)
            if not calendar_id:
                user.selected_calendar_id = None
                session.commit()
                return {"status": "success"}

            verification_warning: str | None = None

            # Verify that the calendar exists in the user's Google Calendar list (if possible)
            if GOOGLE_OAUTH_AVAILABLE:
                try:
                    token_path = get_token_path()
                    if os.path.exists(token_path):
                        service = get_google_calendar_service()
                        calendar_list = service.calendarList().list().execute()
                        calendar_ids = [
                            cal["id"] for cal in calendar_list.get("items", [])
                        ]
                        # Google's primary calendar may not be listed if user has no other calendars? Actually it is.
                        # We'll allow "primary" always.
                        if calendar_id != "primary" and calendar_id not in calendar_ids:
                            raise HTTPException(
                                status_code=400,
                                detail=f"Calendar with ID '{calendar_id}' not found in your Google Calendar list.",
                            )
                except HTTPException:
                    # 400 про "не найден" должен дойти до клиента как есть,
                    # а не превратиться в 500 или в тихий 200.
                    raise
                except Exception as e:
                    # Сеть/токен/квоты — не блокируем сохранение, но говорим об этом.
                    logger.warning(
                        "Failed to verify calendar %r for user %s: %s: %s",
                        calendar_id,
                        current_user.id,
                        type(e).__name__,
                        e,
                    )
                    verification_warning = (
                        f"Настройка сохранена, но проверить календарь в Google "
                        f"не удалось: {type(e).__name__}. "
                        f"Проверьте авторизацию Google и повторите позже."
                    )

            # Look for existing connection
            connection = (
                session.query(GoogleCalendarConnection)
                .filter(
                    GoogleCalendarConnection.user_id == user.id,
                    GoogleCalendarConnection.calendar_id == calendar_id,
                )
                .first()
            )
            now = datetime.now(timezone.utc)
            if connection:
                # Ensure it's enabled
                if not connection.enabled:
                    connection.enabled = 1
                # Do not update connected_at on reconnect
            else:
                # Create new connection
                connection = GoogleCalendarConnection(
                    user_id=user.id,
                    calendar_id=calendar_id,
                    connected_at=now,
                    enabled=1,
                )
                session.add(connection)

            # Update legacy field for backward compatibility
            user.selected_calendar_id = calendar_id

            session.commit()
            user_id = user.id  # ← сохрани id до выхода из with

            # Dispatch в фон: сайт ответит сразу, sync пойдёт после ответа
        background_tasks.add_task(
            GoogleCalendarSyncService.initial_sync_for_user,
            db,
            user_id,
            calendar_id,
        )
        response: dict = {"status": "success"}
        if verification_warning:
            response["warning"] = verification_warning
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Unexpected error in select_google_calendar for user %s",
            current_user.id,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save calendar selection: {str(e)}",
        )


@router.get("/calendar/connections")
async def get_google_calendar_connections(
    current_user: User = Depends(get_current_active_user),
):
    """Get the user's Google Calendar connections."""
    with db.session() as session:
        connections = (
            session.query(GoogleCalendarConnection)
            .filter(GoogleCalendarConnection.user_id == current_user.id)
            .all()
        )
        result = []
        for conn in connections:
            result.append(
                {
                    "calendar_id": conn.calendar_id,
                    "enabled": bool(conn.enabled),
                    "connected_at": conn.connected_at.isoformat()
                    if conn.connected_at
                    else None,
                }
            )
        return {"connections": result}


@router.get("/colors")
async def get_lesson_colors(current_user: User = Depends(get_current_active_user)):
    """Возвращает текущие настройки цветов пользователя."""
    with db.session() as session:
        u = session.query(User).filter(User.id == current_user.id).one()
        return {"colors": u.lesson_colors or {}}


@router.post("/colors")
async def set_lesson_colors(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """Сохраняет пользовательские цвета для типов занятий."""
    try:
        data = await request.json()
        colors = data.get("colors", {})

        if not isinstance(colors, dict):
            raise HTTPException(status_code=400, detail="'colors' must be an object")

        cleaned: dict[str, str | None] = {}
        for key, value in colors.items():
            # Разрешаем только известные типы занятий
            if key not in ALLOWED_LESSON_TYPES:
                continue

            # None = сброс на дефолт
            if value is None:
                continue

            if not isinstance(value, str):
                continue

            # Три допустимых варианта значения:
            #   1. id метки из нашей палитры (xo_os_mango)
            #   2. кастомный HEX (#ff00ff)
            # Числовые colorId (1-11) — устаревший формат, не принимаем
            if value in ALLOWED_PALETTE_IDS or HEX_COLOR_RE.match(value):
                cleaned[key] = value

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()
            user.lesson_colors = cleaned
            session.commit()
            user_id = user.id
            calendar_id = user.selected_calendar_id

        # Если календарь выбран — в фоне синхронизируем метки и патчим события
        if calendar_id:
            background_tasks.add_task(
                GoogleCalendarSyncService.refresh_colors_for_user,
                db,
                user_id,
                calendar_id,
            )

        return {"status": "success"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to set lesson colors for user %s", current_user.id)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save colors: {e}",
        )


@router.get("/colors/palette")
async def get_color_palette(current_user: User = Depends(get_current_active_user)):
    """Возвращает палитру + пользовательские кастомные цвета."""
    with db.session() as session:
        u = session.query(User).filter(User.id == current_user.id).one()
        return {
            "palette": PALETTE_COLORS,
            "custom_slots": CUSTOM_SLOT_KEYS,
            "custom_colors": u.custom_colors or {},
        }


@router.post("/colors/custom")
async def set_custom_colors(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    """Сохраняет кастомные цвета (до 6 слотов)."""
    try:
        data = await request.json()
        custom_colors = data.get("custom_colors") or {}

        if not isinstance(custom_colors, dict):
            raise HTTPException(400, "custom_colors must be an object")

        cleaned: dict = {}
        for slot, payload in custom_colors.items():
            if slot not in CUSTOM_SLOT_KEYS:
                continue
            if not isinstance(payload, dict):
                continue
            hex_val = payload.get("hex")
            name = payload.get("name")
            if not isinstance(hex_val, str) or not _HEX_RE.match(hex_val):
                continue
            cleaned[slot] = {
                "hex": hex_val,
                "name": (name or "")[:40] if isinstance(name, str) else "",
            }

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()
            user.custom_colors = cleaned
            session.commit()
            user_id = user.id
            calendar_id = user.selected_calendar_id

        if calendar_id:
            background_tasks.add_task(
                GoogleCalendarSyncService.refresh_colors_for_user,
                db,
                user_id,
                calendar_id,
            )

        return {"status": "success", "custom_colors": cleaned}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to set custom colors for user %s", current_user.id)
        raise HTTPException(500, f"Failed to save custom colors: {e}")
