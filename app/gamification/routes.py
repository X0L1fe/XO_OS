from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import db
from app.auth.service import get_current_active_user
from .service import get_gamification, update_gamification_settings, reset_gamification

router = APIRouter()


@router.get("/")
def get_gamification(current_user: User = Depends(get_current_active_user)):
    """
    Получите статистику геймификации текущего пользователя (уровень, опыт, серия).
    Это единственный источник истины для отображения геймификации интерфейса.
    """
    with db.session() as session:
        return get_gamification(session, current_user)


@router.put("/settings")
def update_gamification_settings(
    settings: dict,
    current_user: User = Depends(get_current_active_user),
):
    """
    Обновите настройки геймификации для текущего пользователя.
    Сюда входят флаг включения проверки ИИ и значения XP.
    """
    with db.session() as session:
        return update_gamification_settings(session, settings, current_user)


@router.post("/dev/reset")
def reset_gamification_endpoint(
    current_user: User = Depends(get_current_active_user),
):
    """
    Development-only endpoint to reset gamification data for the current user.
    This should not be available in production.
    """
    with db.session() as session:
        return reset_gamification(session, current_user)