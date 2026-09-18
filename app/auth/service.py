import logging
import secrets
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session as SQLAlchemySession

from app.auth.schemas import UserCreate, UserLogin
from app.config import settings
from app.database.models import Session as AppSession
from app.database.models import User, UserStats
from app.email.service import EmailService

logger = logging.getLogger(__name__)

# Try pbkdf2_sha256 if bcrypt has issues
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test if bcrypt works
    pwd_context.hash("test")
except Exception as e:
    print(f"Bcrypt initialization failed: {e}, falling back to pbkdf2_sha256")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    print(f"DEBUG: ENTERING get_password_hash")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_user(
    db: SQLAlchemySession, user: UserCreate, email_service: EmailService
) -> User:
    print(f"DEBUG: create_user called with user")
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )
    print(f"DEBUG: About to call get_password_hash")
    hashed_password = get_password_hash(user.password)

    # Generate verification token
    verification_token = secrets.token_urlsafe(32)
    # Hash the token for storage (like we do with passwords)
    verification_token_hash = get_password_hash(verification_token)
    # Set expiration to 24 hours from now
    verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        is_active=False,  # User is not active until email is verified
        onboarding_completed=False,
        email_verified=False,
        verification_token_hash=verification_token_hash,
        verification_token_expires_at=verification_token_expires_at,
    )
    db.add(db_user)
    db.flush()

    db_stats = UserStats(user_id=db_user.id)
    db.add(db_stats)

    db.commit()
    db.refresh(db_user)

    # Send verification email
    try:
        email_service.send_verification_email(
            email=user.email,
            verification_token=verification_token,
            frontend_url=settings.frontend_url,
        )
        print(f"DEBUG: Verification email sent to {user.email}")
    except Exception as e:
        print(f"DEBUG: Failed to send verification email: {e}")
        # We don't want to fail the registration if email fails,
        # but in a production app we might want to handle this differently

    return db_user


def verify_email(db: SQLAlchemySession, token: str) -> User | None:
    """
    Подтвердите электронную почту с помощью токена и активируйте учетную запись пользователя.

    Args:
        db: БД сессия
        token: токен подтверждения из ссылки электронной почты

    Returns:
        Объект пользователя, если проверка прошла успешно, в противном случае — нет.
    """

    users = db.query(User).filter(User.verification_token_hash.isnot(None)).all()

    for user in users:
        # Проверьте, не истек ли срок действия токена
        if user.verification_token_expires_at:
            # Handle both naive and aware datetimes
            expires = user.verification_token_expires_at
            if expires.tzinfo is None:
                # Assume naive datetime is in UTC
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                # Срок действия токена истек, очистить поля проверки.
                user.verification_token_hash = None
                user.verification_token_expires_at = None
                db.commit()
                continue

        # Подтвердите токен (аналогично проверке пароля)
        if verify_password(token, user.verification_token_hash):
            # Токен действителен, активируйте пользователя
            user.email_verified = True
            user.is_active = True
            # Очистить поля проверки
            user.verification_token_hash = None
            user.verification_token_expires_at = None
            db.commit()
            db.refresh(user)
            return user

    return None


def authenticate_user(db: SQLAlchemySession, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    # Проверьте, подтвержден ли адрес электронной почты
    if not user.email_verified:
        return None
    return user


def update_onboarding_completed(db: SQLAlchemySession, user_id: int) -> None:
    db.query(User).filter(User.id == user_id).update({User.onboarding_completed: True})
    db.commit()


def create_session(
    db: SQLAlchemySession, user_id: int, expires_delta: timedelta = timedelta(days=1)
) -> AppSession:
    # Удалите все существующие сеансы пользователя (чтобы сохранить только один сеанс для каждого пользователя).
    db.query(AppSession).filter(AppSession.user_id == user_id).delete()
    # Создать новый сеанс
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + expires_delta
    db_session = AppSession(user_id=user_id, token=token, expires_at=expires_at)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_user_from_session(
    db: SQLAlchemySession,
    token: str,
) -> User | None:
    session = db.query(AppSession).filter(AppSession.token == token).first()

    if not session:
        return None

    expires_at = session.expires_at

    # SQLite может возвращать DateTime(timezone=True)
    # без tzinfo. В нашем приложении даты сессий
    # создаются в UTC, поэтому naive datetime трактуем как UTC.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    else:
        expires_at = expires_at.astimezone(timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None

    return session.user


def delete_session(db: SQLAlchemySession, token: str) -> None:
    db.query(AppSession).filter(AppSession.token == token).delete()
    db.commit()


def initiate_password_reset(
    db: SQLAlchemySession, email: str, email_service: EmailService, frontend_url: str
) -> bool:
    """
    Инициирует процесс сброса пароля.
    Генерирует токен, сохраняет его хеш и отправляет письмо с ссылкой для сброса пароля.

    Args:
        db: Сессия базы данных
        email: Email пользователя для которого нужно сбросить пароль
        email_service: Сервис для отправки email
        frontend_url: URL фронтенда для формирования ссылки

    Returns:
        True если email найден и процесс инициирован, False иначе
    """
    # Находим пользователя по email
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        # Из соображений безопасности не раскрываем, существует ли email
        # Всегда возвращаем True, чтобы не давать информацию о существующих аккаунтах
        return True

    # Генерируем токен для сброса пароля
    reset_token = secrets.token_urlsafe(32)
    # Хешируем токен для хранения (как делаем с паролями)
    reset_token_hash = get_password_hash(reset_token)
    # Устанавливаем срок действия 1 час
    reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    # Сохраняем хеш токена и срок его действия
    db_user.verification_token_hash = reset_token_hash
    db_user.verification_token_expires_at = reset_token_expires_at
    db.commit()

    # Отправляем email с ссылкой для сброса пароля
    try:
        email_service.send_password_reset_email(
            email=email, reset_token=reset_token, frontend_url=frontend_url
        )
        logger.info(f"Password reset email sent to {email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        # В production может потребоваться иная обработка ошибок
        return False


def verify_and_reset_password(
    db: SQLAlchemySession, token: str, new_password: str
) -> User | None:
    """
    Проверяет токен сброса пароля и устанавливает новый пароль.

    Args:
        db: Сессия базы данных
        token: Токен из ссылки в письме
        new_password: Новый пароль для установки

    Returns:
        Объект пользователя если операция успешна, None иначе
    """
    # Находим пользователя по хешу токена
    users = db.query(User).filter(User.verification_token_hash.isnot(None)).all()

    for user in users:
        # Проверяем, не expired ли токен
        if user.verification_token_expires_at:
            # Handle both naive and aware datetimes
            expires = user.verification_token_expires_at
            if expires.tzinfo is None:
                # Assume naive datetime is in UTC
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                # Токен expired, очищаем поля
                user.verification_token_hash = None
                user.verification_token_expires_at = None
                db.commit()
                continue

        # Проверяем токен (аналогично проверке пароля)
        if verify_password(token, user.verification_token_hash):
            # Токен валидный, устанавливаем новый пароль
            hashed_password = get_password_hash(new_password)
            user.password_hash = hashed_password
            # Очищаем поля токена после использования
            user.verification_token_hash = None
            user.verification_token_expires_at = None
            db.commit()
            db.refresh(user)
            return user

    return None


def initiate_email_change(
    db: SQLAlchemySession,
    user_id: int,
    new_email: str,
    password: str,
    email_service: EmailService,
    frontend_url: str,
) -> bool:
    """
    Инициирует процесс смены email.
    Отправляет подтверждающее письмо на текущий email пользователя.

    Args:
        db: Сессия базы данных
        user_id: ID пользователя
        new_email: Новый email адрес
        email_service: Сервис для отправки email
        frontend_url: URL фронтенда для формирования ссылки

    Returns:
        True если пользователь найден и процесс инициирован, False иначе
    """
    # Находим пользователя по ID
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False

    # Проверяем пароль пользователя
    if not verify_password(password, db_user.password_hash):
        logger.warning(f"Invalid password for user {user_id} during email change initiation")
        return False

    # Проверяем формат нового email
    import re

    if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", new_email):
        return False

    # Генерируем токен для подтверждения смены email
    email_change_token = secrets.token_urlsafe(32)
    # Хешируем токен для хранения
    email_change_token_hash = get_password_hash(email_change_token)
    # Устанавливаем срок действия 24 часа
    email_change_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    # Сохраняем хеш токена, срок действия и новый email (пока ожидает подтверждения)
    db_user.email_change_token_hash = email_change_token_hash
    db_user.email_change_expires_at = email_change_expires_at
    db_user.new_email = new_email
    db.commit()

    # Отправляем подтверждающее письмо на ТЕКУЩИЙ email пользователя
    try:
        confirm_url = (
            f"{frontend_url.rstrip('/')}/change-email?token={email_change_token}"
        )
        email_service.send_email_change_intent_email(
            email=db_user.email,
            email_change_token=email_change_token,
            frontend_url=frontend_url,
            current_email=db_user.email,
            new_email=new_email,
        )
        logger.info(f"Email change confirmation sent to {db_user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email change confirmation: {e}")
        return False


def confirm_email_change(
    db: SQLAlchemySession, token: str, new_email: str, password: str
) -> User | None:
    """
    Подтверждает смену email по токену и обновляет email пользователя.
    Также проверяет, что предоставленный новый email соответствует ожидаемому и что пароль верный.

    Args:
        db: Сессия базы данных
        token: Токен из ссылки в подтверждающем письме
        new_email: Новый email адрес, который пользователь ввел в форме
        password: Текущий пароль пользователя (для подтверждения личности)

    Returns:
        Объект пользователя с обновленным email если операция успешна, None иначе
    """
    # Находим пользователя по хешу токена для смены email
    users = db.query(User).filter(User.email_change_token_hash.isnot(None)).all()

    for user in users:
        # Проверяем, не expired ли токен
        if user.email_change_expires_at:
            # Handle both naive and aware datetimes
            expires = user.email_change_expires_at
            if expires.tzinfo is None:
                # Assume naive datetime is in UTC
                expires = expires.replace(tzinfo=timezone.utc)
            if expires < datetime.now(timezone.utc):
                # Токен expired, очищаем поля
                user.email_change_token_hash = None
                user.email_change_expires_at = None
                user.new_email = None
                db.commit()
                continue

        # Проверяем токен
        if verify_password(token, user.email_change_token_hash):
            # Токен валидный, теперь проверяем, что новый email совпадает с ожидаемым и пароль верный
            if user.new_email != new_email:
                logger.warning(
                    f"Email change token valid but new email mismatch. Expected: {user.new_email}, got: {new_email}"
                )
                return None
            # Проверяем пароль
            if not verify_password(password, user.password_hash):
                logger.warning(
                    f"Email change token valid but password incorrect for user {user.id}"
                )
                return None
            # Все проверки passed, обновляем email
            user.email = user.new_email
            # Очищаем поля после успешного подтверждения
            user.email_change_token_hash = None
            user.email_change_expires_at = None
            user.new_email = None
            db.commit()
            db.refresh(user)
            return user

    return None
