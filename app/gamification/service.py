from sqlalchemy.orm import Session
from typing import Dict

from app.database.models import User, UserStats, FocusEvidence, FocusSession, XPTransaction
from app.event import publish_gamification_updated
from app.auth.service import get_current_active_user  # Not used in service, but kept for consistency if needed


def get_gamification(session: Session, current_user: User) -> dict:
    """
    Получите статистику геймификации текущего пользователя (уровень, опыт, серия).
    Это единственный источник истины для отображения геймификации интерфейса.
    """
    stats = (
        session.query(UserStats)
        .filter(UserStats.user_id == current_user.id)
        .first()
    )
    if not stats:
        # Возвращаем значения по умолчанию, если статистика не существует
        return {
            "level": 1,
            "total_xp": 0,
            "xp_current_level": 0,
            "xp_for_next_level": 1000,
            "xp_remaining": 1000,
            "progress_percent": 0,
            "current_streak": 0,
            "max_streak": 0,
        }

    total_xp = stats.total_xp
    level = stats.level
    current_streak = stats.current_streak
    max_streak = stats.max_streak

    # Рассчитать XP для текущего уровня и прогресса
    xp_for_current_level = (level - 1) * 1000
    xp_current_level = total_xp - xp_for_current_level
    xp_for_next_level = 1000
    xp_remaining = xp_for_next_level - xp_current_level
    progress_percent = (xp_current_level / xp_for_next_level) * 100

    return {
        "level": level,
        "total_xp": total_xp,
        "xp_current_level": xp_current_level,
        "xp_for_next_level": xp_for_next_level,
        "xp_remaining": xp_remaining,
        "progress_percent": round(progress_percent, 2),
        "current_streak": current_streak,
        "max_streak": max_streak,
    }


def update_gamification_settings(session: Session, settings: dict, current_user: User) -> dict:
    """
    Обновите настройки геймификации для текущего пользователя.
    Сюда входят флаг включения проверки ИИ и значения XP.
    """
    user = session.query(User).filter(User.id == current_user.id).first()
    if not user:
        # This should not happen if the dependency works correctly, but we keep the check.
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")

    # Update AI verification enabled setting
    if "ai_verification_enabled" in settings:
        user.ai_verification_enabled = (
            1 if settings["ai_verification_enabled"] else 0
        )

    session.commit()
    return {"message": "Settings updated successfully"}


def reset_gamification(session: Session, current_user: User) -> dict:
    """
    Development-only endpoint to reset gamification data for the current user.
    This should not be available in production.
    """
    # Reset UserStats
    stats = (
        session.query(UserStats)
        .filter(UserStats.user_id == current_user.id)
        .first()
    )
    if stats:
        stats.total_xp = 0
        stats.current_streak = 0
        stats.max_streak = 0
        stats.level = 1
        stats.last_activity_date = None

    # Delete all focus sessions and related data for this user
    # First delete evidence
    session.query(FocusEvidence).join(FocusSession).filter(
        FocusSession.user_id == current_user.id
    ).delete()
    # Then delete XP transactions
    session.query(XPTransaction).filter(
        XPTransaction.user_id == current_user.id
    ).delete()
    # Then delete focus sessions
    session.query(FocusSession).filter(
        FocusSession.user_id == current_user.id
    ).delete()

    session.commit()
    return {"message": "Gamification data reset successfully"}