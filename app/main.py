from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional
from zoneinfo import ZoneInfo

from app.common.schedule_filters import (
    get_schedule_exclusions,
    lesson_is_visible,
    normalize_schedule_category,
)
from app.common.time import msk_now_naive, utc_now
from app.focus.routes import _calculate_elapsed_seconds

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

# Не засоряем вывод INFO-логами сторонних библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

import httpx
from fastapi import (
    BackgroundTasks,
    Body,
    Cookie,
    Depends,
    FastAPI,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.schemas import AuthStatusResponse, UserCreate, UserLogin, UserResponse
from app.auth.service import (
    authenticate_user,
    confirm_email_change,
    create_session,
    create_user,
    delete_session,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    get_user_from_session,
    initiate_email_change,
    initiate_password_reset,
    update_onboarding_completed,
    verify_and_reset_password,
    verify_password,
)
from app.auth.service import (
    verify_email as verify_email_service,
)
from app.config import Settings
from app.database.db import Database
from app.database.models import (
    FocusEvidence,
    FocusSession,
    Lesson,
    Notification,
    ScheduleExclusion,
    User,
    UserStats,
    XPTransaction,
)
from app.email.service import EmailService
from app.event import (
    event_publisher,
    publish_focus_updated,
    publish_gamification_updated,
)
from app.focus import router as focus_router

# Import for focus session service
from app.focus.service import FocusService
from app.gamification import router as gamification_router
from app.mais_parser import (
    async_fetch_group_schedule,
    async_fetch_groups,
    fetch_group_schedule,
    fetch_groups,
    parse_mais_schedule,
)
from app.schedule import router as schedule_router
from app.stats import router as stats_router
from app.sync.service import SyncService
from app.telegram.schemas import (
    TelegramLinkResponse,
    TelegramStatusResponse,
    TelegramUnlinkResponse,
)
from app.telegram.service import (
    create_telegram_link_code,
    unlink_telegram_account,
)

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

app = FastAPI(title="XO_OS", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://192.168.1.2/:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

db = Database()
settings = Settings()
# Obsidian vault path configuration
OBSIDIAN_CONFIG_PATH = Path("data/obsidian_config.json")

# Server-Sent Events for real-time updates
# We'll use a simple in-memory dictionary to track active connections
# In a production app, you would use a proper message queue like Redis Pub/Sub

app.include_router(stats_router, prefix="/api/stats")
app.include_router(gamification_router, prefix="/api/gamification")
app.include_router(focus_router, prefix="/api/focus")
app.include_router(schedule_router, prefix="/api/schedule")

# ============================================================
# DEVELOPMENT ONLY: RESET GAMIFICATION
# ============================================================


@app.post("/api/webhook/telegram")
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


def get_obsidian_vault_path() -> Optional[str]:
    if OBSIDIAN_CONFIG_PATH.is_file():
        try:
            data = json.loads(OBSIDIAN_CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("vault_path")
        except Exception:
            return None
    return None


def save_obsidian_vault_path(path: str) -> None:
    OBSIDIAN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"vault_path": path}
    OBSIDIAN_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


# Serve static files (frontend) if directory exists
frontend_dir = Path(__file__).parent / "web"
if frontend_dir.is_dir():
    # We'll serve static files via a catch-all route below
    pass


# API routes under /api prefix
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "XO_OS"}


@app.post("/api/export")
async def export_to_obsidian(
    vault: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Экспортируйте занятия в Obsidian.
    """
    try:
        vault_path = (
            vault or get_obsidian_vault_path() or os.getenv("OBSIDIAN_VAULT_PATH")
        )
        if not vault_path:
            return {
                "status": "error",
                "message": "Obsidian vault path not provided. Set OBSIDIAN_VAULT_PATH environment variable, save via /api/obsidian/path, or pass 'vault' parameter.",
            }
        exported = SyncService(db).export_to_obsidian(vault_path)
        return {
            "status": "success",
            "exported": exported,
            "message": f"Exported {exported} lessons to Obsidian vault at {vault_path}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to export to Obsidian: {str(e)}"}


@app.post("/api/auth/register")
async def register(user: UserCreate) -> Response:
    """Register a new user."""
    try:
        print(f"DEBUG: ENTERING TRY BLOCK")
        print(f"DEBUG: About to call create_user")
        with db.session() as db_session:
            # Initialize email service
            email_service = EmailService(settings)
            db_user = create_user(db_session, user, email_service)
            # Do NOT auto-login - user must verify email first
            # Build user response manually to avoid potential serialization issues
            user_data = {
                "id": db_user.id,
                "name": db_user.name,
                "email": db_user.email,
                "onboarding_completed": bool(db_user.onboarding_completed),
            }
            response = {
                "success": True,
                "message": "Проверочное письмо отправлено на вашу электронную почту. Пожалуйста, проверьте письмо и перейдите по ссылке для подтверждения аккаунта.",
                "user": user_data,
            }
            res = Response(content=json.dumps(response), media_type="application/json")
            return res

    except HTTPException:
        raise

    except Exception as e:
        # Log the exception for debugging
        print(f"Registration error: {e}")
        import traceback

        traceback.print_exc()

        res = Response(
            content=json.dumps(
                {
                    "detail": str(e),
                    "type": type(e).__name__,
                }
            ),
            media_type="application/json",
            status_code=500,
        )
        return res


@app.get("/api/auth/verify-email")
async def verify_email(token: str = Query(...)) -> Response:
    """Verify email using token from verification link."""
    try:
        with db.session() as db_session:
            db_user = verify_email_service(db_session, token)
            if db_user:
                # Email verified successfully, create session and log user in
                db_session_obj = create_session(db_session, db_user.id)
                response = {
                    "success": True,
                    "message": "Электронная почта успешно подтверждена! Вы вошли в систему.",
                    "user": UserResponse.model_validate(db_user).model_dump(),
                }
                res = Response(
                    content=json.dumps(response), media_type="application/json"
                )
                res.set_cookie(
                    key="session_token",
                    value=db_session_obj.token,
                    httponly=True,
                    max_age=86400,  # 1 day
                    samesite="lax",
                    path="/",
                )
                return res
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недействительный или истёкший токен подтверждения",
                )

    except HTTPException:
        raise

    except Exception as e:
        # Log the exception for debugging
        print(f"Email verification error: {e}")
        import traceback

        traceback.print_exc()

        res = Response(
            content=json.dumps(
                {
                    "detail": str(e),
                    "type": type(e).__name__,
                }
            ),
            media_type="application/json",
            status_code=500,
        )
        return res


@app.post("/api/auth/resend-verification")
async def resend_verification(email: str = Body(..., embed=True)) -> Response:
    """Resend verification email to user."""
    try:
        with db.session() as db_session:
            # Find user by email
            db_user = db_session.query(User).filter(User.email == email).first()
            if not db_user:
                # Don't reveal that email doesn't exist for security
                return Response(
                    content=json.dumps(
                        {
                            "success": True,
                            "message": "Если email существует в системе, письмо с подтверждением было отправлено",
                        }
                    ),
                    media_type="application/json",
                )

            # Check if already verified
            if db_user.email_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Электронная почта уже подтверждена",
                )

            # Initialize email service
            email_service = EmailService(settings)

            # Generate new verification token
            verification_token = secrets.token_urlsafe(32)
            # Hash the token for storage (like we do with passwords)
            verification_token_hash = get_password_hash(verification_token)
            # Set expiration to 24 hours from now
            verification_token_expires_at = utc_now() + timedelta(hours=24)

            # Update user with new token
            db_user.verification_token_hash = verification_token_hash
            db_user.verification_token_expires_at = verification_token_expires_at
            db_session.commit()

            # Send verification email
            try:
                email_service.send_verification_email(
                    email=email,
                    verification_token=verification_token,
                    frontend_url=settings.frontend_url,
                )
                print(f"DEBUG: Resent verification email to {email}")
            except Exception as e:
                print(f"DEBUG: Failed to send verification email: {e}")
                # We don't want to fail the resend if email fails,
                # but in a production app we might want to handle this differently

            return Response(
                content=json.dumps(
                    {
                        "success": True,
                        "message": "Проверочное письмо отправлено на вашу электронную почту",
                    }
                ),
                media_type="application/json",
            )

    except HTTPException:
        raise

    except Exception as e:
        # Log the exception for debugging
        print(f"Resend verification error: {e}")
        import traceback

        traceback.print_exc()

        res = Response(
            content=json.dumps(
                {
                    "detail": str(e),
                    "type": type(e).__name__,
                }
            ),
            media_type="application/json",
            status_code=500,
        )
        return res


@app.post("/api/auth/login")
async def login(user: UserLogin) -> Response:
    """Log in a user."""
    with db.session() as db_session:
        db_user = authenticate_user(db_session, user.email, user.password)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Create a session
        db_session_obj = create_session(db_session, db_user.id)
        response = {
            "success": True,
            "user": UserResponse.model_validate(db_user).model_dump(),
        }
        res = Response(content=json.dumps(response), media_type="application/json")
        res.set_cookie(
            key="session_token",
            value=db_session_obj.token,
            httponly=True,
            max_age=86400,  # 1 day
            samesite="lax",
            path="/",
        )
        return res


@app.post("/api/auth/logout")
async def logout(
    session_token: Optional[str] = Cookie(None),
    current_user: Optional[User] = Depends(get_current_user),
) -> dict[str, Any]:
    """Log out the current user."""
    with db.session() as db_session:
        if session_token:
            delete_session(db_session, session_token)
        # Clear the cookie
        from fastapi import Response

        res = Response(
            content=json.dumps({"success": True}), media_type="application/json"
        )
        res.delete_cookie(key="session_token", path="/")
        return res


@app.get("/api/auth/me")
async def get_current_user_info(
    current_user: Optional[User] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get the current user."""
    if not current_user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": UserResponse.model_validate(current_user)}


@app.get("/api/auth/status")
async def auth_status(
    current_user: Optional[User] = Depends(get_current_user),
) -> AuthStatusResponse:
    """Check authentication status."""
    if not current_user:
        return AuthStatusResponse(
            authenticated=False, user=None, onboarding_completed=False
        )
    return AuthStatusResponse(
        authenticated=True,
        user=UserResponse.model_validate(current_user),
        onboarding_completed=current_user.onboarding_completed,
    )


# NEW ENDPOINTS FOR PASSWORD RESET AND EMAIL CHANGE


@app.post("/api/auth/initiate-password-reset")
async def initiate_password_reset_endpoint(
    email: str = Body(..., embed=True),
) -> Response:
    """Initiate password reset process."""
    try:
        with db.session() as db_session:
            email_service = EmailService(settings)
            success = initiate_password_reset(
                db_session, email, email_service, settings.frontend_url
            )
            # Always return success for security (to not leak whether email exists)
            return Response(
                content=json.dumps(
                    {
                        "success": True,
                        "message": "Если email существует в системе, письмо с инструкциями по сбросу пароля было отправлено",
                    }
                ),
                media_type="application/json",
            )
    except Exception as e:
        print(f"Initiate password reset error: {e}")
        import traceback

        traceback.print_exc()
        return Response(
            content=json.dumps(
                {
                    "success": True,
                    "message": "Если email существует в системе, письмо с инструкциями по сбросу пароля было отправлено",
                }
            ),
            media_type="application/json",
        )


@app.post("/api/auth/reset-password")
async def reset_password_endpoint(
    token: str = Body(..., embed=True), new_password: str = Body(..., embed=True)
) -> Response:
    """Reset password using token and new password."""
    try:
        with db.session() as db_session:
            db_user = verify_and_reset_password(db_session, token, new_password)
            if db_user:
                # Password reset successful, create session and log user in
                db_session_obj = create_session(db_session, db_user.id)
                response = {
                    "success": True,
                    "message": "Пароль успешно изменён! Вы вошли в систему.",
                    "user": UserResponse.model_validate(db_user).model_dump(),
                }
                res = Response(
                    content=json.dumps(response), media_type="application/json"
                )
                res.set_cookie(
                    key="session_token",
                    value=db_session_obj.token,
                    httponly=True,
                    max_age=86400,  # 1 day
                    samesite="lax",
                    path="/",
                )
                return res
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недействительный или истёкший токен сброса пароля",
                )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@app.post("/api/auth/initiate-email-change")
async def initiate_email_change_endpoint(
    new_email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    """Initiate email change process (requires current authentication)."""
    try:
        with db.session() as db_session:
            email_service = EmailService(settings)
            success = initiate_email_change(
                db_session,
                current_user.id,
                new_email,
                password,
                email_service,
                settings.frontend_url,
            )
            if success:
                return Response(
                    content=json.dumps(
                        {
                            "success": True,
                            "message": "Письмо с подтверждением отправлено на ваш текущий email. Пожалуйста, проверьте почту и перейдите по ссылке для подтверждения смены email.",
                        }
                    ),
                    media_type="application/json",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Не удалось инициировать смену email. Проверьте формат нового email или попробуйте позже.",
                )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Initiate email change error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


@app.post("/api/auth/confirm-email-change")
async def confirm_email_change_endpoint(
    token: str = Body(..., embed=True),
    new_email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
) -> Response:
    """Confirm email change using token, new email, and current password."""
    try:
        with db.session() as db_session:
            db_user = confirm_email_change(db_session, token, new_email, password)
            if db_user:
                # Email change successful
                return Response(
                    content=json.dumps(
                        {
                            "success": True,
                            "message": "Email успешно изменён!",
                            "user": UserResponse.model_validate(db_user).model_dump(),
                        }
                    ),
                    media_type="application/json",
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Недействительный или истёкший токен, неверный email или пароль",
                )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Confirm email change error: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Внутренняя ошибка сервера",
        )


# Additional API routes


@app.get("/api/events")
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


@app.get("/api/now")
def get_now(
    current_user: User = Depends(get_current_active_user),
):
    """
    Верните текущее состояние NowBlock.
    Это может быть:
      - Активный или приостановленный сеанс фокусировки (с подробностями)
      - Текущий видимый урок (если есть), когда ни один сеанс фокусировки не активен.
      - Состояние ожидания (нет урока, нет фокус-сессии)
    """
    with db.session() as session:
        focus_service = FocusService(session)
        now = msk_now_naive()

        current_session = focus_service.get_current_session(user_id=current_user.id)

        # Fallback: недавно завершённая сессия — показываем её 30 минут,
        # чтобы пользователь увидел результат AI-проверки и начисленный XP.
        if not current_session:
            recent_cutoff = now - timedelta(minutes=30)
            current_session = (
                session.query(FocusSession)
                .filter(
                    FocusSession.user_id == current_user.id,
                    FocusSession.status == "completed",
                    FocusSession.ended_at.isnot(None),
                    FocusSession.ended_at >= recent_cutoff,
                )
                .order_by(FocusSession.ended_at.desc())
                .first()
            )

        if current_session:
            elapsed_seconds = _calculate_elapsed_seconds(current_session)

            lesson = None
            if current_session.lesson_id:
                lesson = (
                    session.query(Lesson)
                    .filter(Lesson.id == current_session.lesson_id)
                    .first()
                )

            lesson_subject = lesson.subject if lesson else ""
            lesson_description = lesson.description if lesson else ""

            return {
                "type": "focus",
                "session_id": current_session.id,
                "status": current_session.status,
                "lesson_id": current_session.lesson_id,
                "lesson_subject": lesson_subject,
                "lesson_description": lesson_description,
                "goal_text": current_session.goal_text,
                "started_at": current_session.started_at,
                "ended_at": current_session.ended_at,  # ← обязательно
                "elapsed_seconds": elapsed_seconds,
                "duration_seconds": current_session.duration_seconds,  # ← обязательно
                "completion_mode": current_session.completion_mode,  # ← обязательно
                "verification_status": current_session.verification_status,  # ← вот это
                "xp_awarded": current_session.xp_awarded,  # ← и это
                "evidence_provided": bool(current_session.evidence_provided),
            }

        # No active focus session, check for the current visible lesson
        excluded_categories, excluded_subjects = get_schedule_exclusions(
            session,
            current_user.id,
        )

        lessons = (
            session.query(Lesson)
            .filter(
                Lesson.user_id == current_user.id,
                Lesson.start_time <= now,
                Lesson.end_time >= now,
            )
            .order_by(Lesson.start_time)
            .all()
        )

        lesson = next(
            (
                item
                for item in lessons
                if lesson_is_visible(
                    item,
                    excluded_categories,
                    excluded_subjects,
                )
            ),
            None,
        )

        if lesson:
            category = normalize_schedule_category(lesson.category)
            return {
                "type": "lesson",
                "lesson_id": lesson.id,
                "lesson_subject": lesson.subject or "",
                "lesson_description": lesson.description or "",
                "time_estimate": (
                    f"{lesson.start_time.strftime('%H:%M')} - "
                    f"{lesson.end_time.strftime('%H:%M')}"
                ),
                "category": category,
            }

        # No active focus session and no current lesson
        return {"type": "idle"}


# ============================================================
# STATISTICS
# ============================================================


@app.get("/api/achievements")
def get_achievements(current_user: User = Depends(get_current_active_user)):
    """Get achievements based on stats."""
    with db.session() as session:
        stats = (
            session.query(UserStats)
            .filter(UserStats.user_id == current_user.id)
            .first()
        )
        if not stats:
            stats = UserStats(user_id=current_user.id)
            session.add(stats)
            session.commit()
        achievements = []
        # Streak achievements
        if stats.current_streak >= 7:
            achievements.append(f"Стаж {stats.current_streak} дней")
        if stats.current_streak >= 30:
            achievements.append(f"Стаж {stats.current_streak} дней")
        # Level achievements
        if stats.level >= 1:
            achievements.append(f"Уровень {stats.level}")
        if stats.level >= 5:
            achievements.append(f"Уровень {stats.level}")
        if stats.level >= 10:
            achievements.append(f"Уровень {stats.level}")
        # XP achievements
        if stats.total_xp >= 1000:
            achievements.append("Новичок")
        if stats.total_xp >= 5000:
            achievements.append("Опытный")
        if stats.total_xp >= 10000:
            achievements.append("Ветеран")
        return {"achievements": achievements, "streak": stats.current_streak}


@app.get("/api/calendar/status")
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


@app.get("/api/obsidian/status")
def get_obsidian_status():
    """Get obsidian status."""
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault_path:
        return {"status": "ready"}
    return {"status": "not_configured"}


class ObsidianPath(BaseModel):
    vault: str


@app.get("/api/obsidian/path")
def get_obsidian_path():
    """Get saved Obsidian vault path."""
    path = get_obsidian_vault_path()
    if path is None:
        return {"path": ""}
    return {"path": path}


@app.post("/api/obsidian/path")
def set_obsidian_path(data: ObsidianPath):
    """Save Obsidian vault path."""
    vault = data.vault
    if not vault or not vault.strip():
        raise HTTPException(
            status_code=400, detail="Obsidian vault path cannot be empty"
        )
    vault = vault.strip()
    save_obsidian_vault_path(vault)
    return {"status": "success", "path": vault}


@app.get("/api/mais/groups")
def get_mais_groups():
    """Get list of MAIS groups."""
    try:
        groups = fetch_groups()
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch groups: {e}")


@app.post("/api/mais/import")
def import_mais_schedule(
    group_name: str = Form(...), current_user: User = Depends(get_current_active_user)
):
    """Import schedule for a given MAIS group name."""
    try:
        # Fetch schedule JSON
        json_bytes = fetch_group_schedule(group_name)
        # Parse into LessonData
        lessons = parse_mais_schedule(json_bytes, group_name=group_name)
        # Import using SyncService
        # Try to create Google Calendar service if user has selected a calendar and is authenticated
        google_calendar_service = None
        try:
            # Check if the user has a selected calendar (not the default? but we always have one)
            # and if we can authenticate with Google Calendar
            if current_user.selected_calendar_id:
                google_calendar_service = GoogleCalendarSyncService(
                    db,
                    calendar_id=current_user.selected_calendar_id,
                    user_id=current_user.id,
                )
        except Exception as e:
            # If we fail to create the service, log it and continue without Google Calendar sync
            print(f"Failed to initialize Google Calendar service: {e}")
            google_calendar_service = None

        sync_service = SyncService(db, google_calendar_service=google_calendar_service)
        result = sync_service.import_lesson_data(
            lessons, user_id=current_user.id, mais_group_id=group_name
        )
        return {
            "status": "success",
            "group": group_name,
            "parsed": result.parsed,
            "created": result.created,
            "updated": result.updated,
            "moved": result.moved,
            "deleted": result.deleted,
            "unchanged": result.unchanged,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import schedule for group '{group_name}': {e}",
        )


@app.post("/api/mais/group")
def set_mais_group(
    group_name: str = Form(...), current_user: User = Depends(get_current_active_user)
):
    """Set the MAIS group for the current user."""
    # Optionally, you could validate that the group exists by calling fetch_groups() and checking.
    # For now, we just save the group name.
    with db.session() as session:
        user = session.query(User).filter(User.id == current_user.id).one()
        user.mais_group_id = group_name
        user.onboarding_completed = True
        session.commit()
    return {"status": "success", "group": group_name}


@app.get("/api/google/calendars")
async def get_google_calendars(
    current_user: User = Depends(get_current_active_user),
):
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


@app.post("/api/onboarding/complete")
async def complete_onboarding(
    request: Request, current_user: User = Depends(get_current_active_user)
):
    """Complete onboarding by saving group and calendar selection."""
    try:
        data = await request.json()
        group_name = data.get("group_name")
        calendar_id = data.get("calendar_id", "primary")

        if not group_name:
            raise HTTPException(status_code=400, detail="Group name is required")

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()
            user.mais_group_id = group_name
            user.selected_calendar_id = calendar_id
            user.onboarding_completed = True
            session.commit()
        return {"status": "success"}
    except Exception as e:
        # Log the error for debugging
        print(f"Error in complete_onboarding: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to complete onboarding: {str(e)}"
        )


@app.post("/api/google/calendar/select")
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
        print(f"Error in select_google_calendar: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to save calendar selection: {str(e)}"
        )


# Google OAuth endpoints
@app.get("/api/google/auth")
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


@app.get("/api/google/callback")
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


@app.get("/api/google/status")
async def google_status(current_user: User = Depends(get_current_user)):
    """Check Google connection status and last sync time."""
    if not GOOGLE_OAUTH_AVAILABLE:
        return {"connected": False, "error": "Google OAuth not available"}
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
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
                from google.auth.transport.requests import Request

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


@app.post("/api/google/disconnect")
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


@app.post("/api/debug/echo")
async def echo(request: Request):
    body = await request.body()
    try:
        decoded = body.decode("utf-8")
    except UnicodeDecodeError:
        decoded = body.decode("utf-8", errors="replace")
    return {"body": decoded, "body_bytes": list(body)}


@app.get("/api/mais/import_get")
def import_mais_schedule_get(group_name: str):
    """Get the group name as a test."""
    return {"group_name": group_name}


# ============================================================
# TELEGRAM
# ============================================================


@app.post(
    "/api/telegram/link",
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

    bot_username = Settings.telegram_bot_username.strip().lstrip("@")

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


@app.get(
    "/api/telegram/status",
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


@app.post(
    "/api/telegram/unlink",
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


# Notification endpoints
@app.get("/api/notifications")
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
) -> list[dict]:
    """
    Get notifications for the current user.
    Returns a list of notifications sorted by creation date (newest first).
    """
    with db.session() as session:
        notifications = (
            session.query(Notification)
            .filter(Notification.user_id == current_user.id)
            .order_by(Notification.created_at.desc())
            .all()
        )
        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "is_read": bool(n.is_read),
                "type": n.type,
                "related_id": n.related_id,
                "related_type": n.related_type,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ]


@app.post("/api/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    """
    Mark a notification as read.
    """
    with db.session() as session:
        notification = (
            session.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == current_user.id,
            )
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        notification.is_read = True
        session.commit()
        return {"success": True}


@app.post("/api/notifications/toggle")
async def toggle_notifications_enabled(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    """
    Toggle notifications enabled for the current user.
    """
    with db.session() as session:
        user = session.query(User).filter(User.id == current_user.id).one()
        user.notifications_enabled = not user.notifications_enabled
        session.commit()
        return {"enabled": bool(user.notifications_enabled)}


# Trigger reload


# Background task for periodic MAIS schedule checking
async def check_mais_schedule_for_user(user: User, session: Session) -> None:
    """
    Check for schedule changes for a specific user and create notifications if changes are found.
    """
    try:
        # Fetch schedule JSON from MAIS
        json_bytes = await async_fetch_group_schedule(user.mais_group_id)
        # Parse into LessonData
        lessons = parse_mais_schedule(json_bytes, group_name=user.mais_group_id)
        # Import using SyncService (this will sync with Google Calendar and return a DiffResult)
        # Try to create Google Calendar service if user has selected a calendar and is authenticated
        google_calendar_service = None
        try:
            # Check if the user has a selected calendar (not the default? but we always have one)
            # and if we can authenticate with Google Calendar
            if user.selected_calendar_id:
                google_calendar_service = GoogleCalendarSyncService(
                    db,
                    calendar_id=user.selected_calendar_id,
                    user_id=user.id,
                )
        except Exception as e:
            # If we fail to create the service, log it and continue without Google Calendar sync
            print(
                f"Failed to initialize Google Calendar service for user {user.id}: {e}"
            )
            google_calendar_service = None

        sync_service = SyncService(db, google_calendar_service=google_calendar_service)
        result = sync_service.import_lesson_data(
            lessons, user_id=user.id, mais_group_id=user.mais_group_id
        )
        # If we have a Google Calendar service, update the last synced time
        if google_calendar_service is not None:
            user.last_synced_at = utc_now()
        # Check if there are any changes
        has_changes = (
            result.created > 0
            or result.updated > 0
            or result.moved > 0
            or result.deleted > 0
        )
        if has_changes:
            # Prepare notification message
            message_parts = []
            if result.created:
                message_parts.append(f"добавлено: {result.created}")
            if result.updated:
                message_parts.append(f"обновлено: {result.updated}")
            if result.moved:
                message_parts.append(f"перемещено: {result.moved}")
            if result.deleted:
                message_parts.append(f"удалено: {result.deleted}")
            message = "Изменения в расписании: " + ", ".join(message_parts)
            # Create notification
            notification = Notification(
                user_id=user.id,
                title="Изменения в расписании",
                message=message,
                type="schedule_change",
            )
            session.add(notification)
            # Send Telegram notification if user has Telegram linked and notifications are enabled
            if user.telegram_id is not None and user.notifications_enabled:
                try:
                    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
                    if telegram_token:
                        telegram_url = (
                            f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                        )
                        payload = {
                            "chat_id": user.telegram_id,
                            "text": f"🔔 {notification.title}\n{notification.message}",
                        }
                        async with httpx.AsyncClient() as client:
                            await client.post(telegram_url, json=payload)
                except Exception as e:
                    # Log error but don't break the flow
                    print(f"Failed to send Telegram notification: {e}")
    except Exception as e:
        # Log error but don't break the background task
        print(f"Error checking MAIS schedule for user {user.id}: {e}")
        import traceback

        traceback.print_exc()


async def periodic_mais_check():
    """
    Background task that periodically checks for MAIS schedule changes for all users.
    """
    interval = 3600  # seconds (1 hour)
    while True:
        try:
            # Get all users that have a mais_group_id and notifications enabled
            with db.session() as session:
                users = (
                    session.query(User)
                    .filter(
                        User.mais_group_id.isnot(None),
                        User.notifications_enabled == True,
                    )
                    .all()
                )
            # For each user, check if it's time to check
            for user in users:
                # We'll open a new session for each user to avoid holding a long session
                with db.session() as session:
                    # Re-fetch the user in this session to get the latest state
                    user_db = session.query(User).filter(User.id == user.id).one()
                    # Check if we need to run the check
                    now = utc_now()
                    last_mais_check = user_db.last_mais_check
                    if last_mais_check is not None:
                        # Ensure last_mais_check is offset-aware in UTC for subtraction
                        if last_mais_check.tzinfo is None:
                            last_mais_check = last_mais_check.replace(
                                tzinfo=timezone.utc
                            )
                        else:
                            last_mais_check = last_mais_check.astimezone(timezone.utc)

                    if (
                        user_db.last_mais_check is None
                        or (now - last_mais_check).total_seconds() >= interval
                    ):
                        # Perform the check
                        await check_mais_schedule_for_user(user_db, session)
                        # Update the last check time
                        user_db.last_mais_check = now
                        # Commit the session (notification and last_mais_check)
                        session.commit()
        except Exception as e:
            # Log the error and continue
            print(f"Error in periodic MAIS check: {e}")
            import traceback

            traceback.print_exc()
        # Wait for the next interval
        await asyncio.sleep(interval)


# Startup event to launch the background task
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(periodic_mais_check())


# Catch-all route for serving frontend (if exists)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # Не перехватываем API-пути
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404, detail="Not Found")

    # Если запрошен реальный файл — отдаём его
    file_path = frontend_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)

    # Иначе — SPA-роут
    return FileResponse(frontend_dir / "index.html")
