from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.service import get_current_active_user
from app.database.db import db
from app.database.models import Notification, User

router = APIRouter()


@router.get("/notifications")
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


@router.post("/notifications/{notification_id}/read")
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


@router.post("/notifications/toggle")
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


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """Возвращает количество непрочитанных уведомлений."""
    with db.session() as session:
        count = (
            session.query(Notification)
            .filter(
                Notification.user_id == current_user.id,
                Notification.is_read == 0,
            )
            .count()
        )
        return {"count": count}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    """Помечает все уведомления пользователя прочитанными."""
    with db.session() as session:
        session.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == 0,
        ).update({"is_read": 1})
        session.commit()
        return {"success": True}


@router.delete("/notifications")
async def delete_all_notifications(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    """Удаляет ВСЕ уведомления пользователя."""
    with db.session() as session:
        session.query(Notification).filter(
            Notification.user_id == current_user.id,
        ).delete()
        session.commit()
        return {"success": True}


@router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, bool]:
    """Удаляет уведомление пользователя."""
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
        session.delete(notification)
        session.commit()
        return {"success": True}
