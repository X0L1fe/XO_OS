from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException
from app.mais_parser import fetch_groups, fetch_group_schedule, parse_mais_schedule
from app.auth.service import get_current_active_user
from app.database.models import User
from app.database.db import db
from app.google_calendar.service import GoogleCalendarSyncService
from app.sync.service import SyncService

router = APIRouter()


@router.get("/mais/groups")
def get_mais_groups():
    """Get list of MAIS groups."""
    try:
        groups = fetch_groups()
        return {"groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch groups: {e}")


@router.post("/mais/import")
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


@router.post("/mais/group")
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


@router.get("/mais/import_get")
def import_mais_schedule_get(group_name: str):
    """Get the group name as a test."""
    return {"group_name": group_name}