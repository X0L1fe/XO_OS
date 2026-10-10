from __future__ import annotations

import asyncio
import os
import traceback
from datetime import timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.common.time import utc_now
from app.database.db import db
from app.database.models import Notification, User
from app.mais_parser import async_fetch_group_schedule, parse_mais_schedule
from app.sync.service import SyncService

# Try to import Google Calendar service; if not available, set to None.
try:
    from google_auth_oauthlib.flow import Flow

    from app.google_calendar.service import GoogleCalendarSyncService

    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GoogleCalendarSyncService = None
    GOOGLE_OAUTH_AVAILABLE = False


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
        result = await asyncio.to_thread(
            sync_service.import_lesson_data,
            lessons,
            user_id=user.id,
            mais_group_id=user.mais_group_id,
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


async def periodic_mais_check() -> None:
    """
    Background task that periodically checks for MAIS schedule changes for all users.
    """
    interval = 3600  # seconds (1 hour)
    await asyncio.sleep(30)
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
