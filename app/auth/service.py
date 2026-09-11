
from passlib.context import CryptContext
from sqlalchemy.orm import Session as SQLAlchemySession
from app.database.models import User, UserStats, Session as AppSession
from app.auth.schemas import UserCreate, UserLogin
from fastapi import HTTPException, status
import secrets
from datetime import datetime, timezone, timedelta

# Try pbkdf2_sha256 if bcrypt has issues
try:
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    # Test if bcrypt works
    pwd_context.hash("test")
except Exception as e:
    print(f"Bcrypt initialization failed: {e}, falling back to pbkdf2_sha256")
    pwd_context = CryptContext(schemes=['pbkdf2_sha256'], deprecated='auto')

def get_password_hash(password: str) -> str:
    print(f"DEBUG: ENTERING get_password_hash")
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: SQLAlchemySession, user: UserCreate) -> User:
    print(f"DEBUG: create_user called with user")
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Пользователь с таким email уже существует'
        )
    print(f"DEBUG: About to call get_password_hash")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        is_active=True,
        onboarding_completed=False
    )
    db.add(db_user)
    db.flush()

    db_stats = UserStats(user_id=db_user.id)
    db.add(db_stats)

    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: SQLAlchemySession, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def update_onboarding_completed(db: SQLAlchemySession, user_id: int) -> None:
    db.query(User).filter(User.id == user_id).update({User.onboarding_completed: True})
    db.commit()

def create_session(db: SQLAlchemySession, user_id: int, expires_delta: timedelta = timedelta(days=1)) -> AppSession:
    # Delete any existing sessions for the user (to keep only one session per user, or we can allow multiple)
    db.query(AppSession).filter(AppSession.user_id == user_id).delete()
    # Create a new session
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + expires_delta
    db_session = AppSession(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

from datetime import datetime, timezone


def get_user_from_session(
    db: SQLAlchemySession,
    token: str,
    ) -> User | None:
    session = (
        db.query(AppSession)
        .filter(AppSession.token == token)
        .first()
    )

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

