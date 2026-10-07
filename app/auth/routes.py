from __future__ import annotations

import json
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

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
    UploadFile,
    status,
)
from fastapi.responses import JSONResponse
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
    verify_email as verify_email_service,
)
from app.config import Settings
from app.common.time import utc_now
from app.database.db import Database
from app.database.models import User
from app.email.service import EmailService

logger = logging.getLogger(__name__)

# Router for auth endpoints
router = APIRouter()


@router.post("/register")
async def register(user: UserCreate) -> Response:
    """Register a new user."""
    try:
        print(f"DEBUG: ENTERING TRY BLOCK")
        print(f"DEBUG: About to call create_user")
        db = Database()
        settings = Settings()
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


@router.get("/verify-email")
async def verify_email(token: str = Query(...)) -> Response:
    """Verify email using token from verification link."""
    try:
        db = Database()
        settings = Settings()
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


@router.post("/resend-verification")
async def resend_verification(email: str = Body(..., embed=True)) -> Response:
    """Resend verification email to user."""
    try:
        db = Database()
        settings = Settings()
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


@router.post("/login")
async def login(user: UserLogin) -> Response:
    """Log in a user."""
    db = Database()
    settings = Settings()
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


@router.post("/logout")
async def logout(
    session_token: Optional[str] = Cookie(None),
    current_user: Optional[User] = Depends(get_current_user),
) -> dict[str, Any]:
    """Log out the current user."""
    db = Database()
    settings = Settings()
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


@router.get("/me")
async def get_current_user_info(
    current_user: Optional[User] = Depends(get_current_user),
) -> dict[str, Any]:
    """Get the current user."""
    db = Database()
    settings = Settings()
    if not current_user:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": UserResponse.model_validate(current_user)}


@router.get("/status")
async def auth_status(
    current_user: Optional[User] = Depends(get_current_user),
) -> AuthStatusResponse:
    """Check authentication status."""
    db = Database()
    settings = Settings()
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


@router.post("/initiate-password-reset")
async def initiate_password_reset_endpoint(
    email: str = Body(..., embed=True),
) -> Response:
    """Initiate password reset process."""
    try:
        db = Database()
        settings = Settings()
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


@router.post("/reset-password")
async def reset_password_endpoint(
    token: str = Body(..., embed=True), new_password: str = Body(..., embed=True)
) -> Response:
    """Reset password using token and new password."""
    try:
        db = Database()
        settings = Settings()
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


@router.post("/initiate-email-change")
async def initiate_email_change_endpoint(
    new_email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    """Initiate email change process (requires current authentication)."""
    try:
        db = Database()
        settings = Settings()
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


@router.post("/confirm-email-change")
async def confirm_email_change_endpoint(
    token: str = Body(..., embed=True),
    new_email: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
) -> Response:
    """Confirm email change using token, new email, and current password."""
    try:
        db = Database()
        settings = Settings()
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