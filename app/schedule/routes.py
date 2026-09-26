from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.service import get_current_active_user
from app.database.db import db
from app.schedule.service import ScheduleService

router = APIRouter()


@router.get("/filters")
def get_schedule_filters(
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get the user's schedule exclusion filters.
    """
    with db.session() as session:
        service = ScheduleService(session)
        return service.get_filter_data(current_user["id"])


@router.put("/filters")
def update_schedule_filters(
    excluded_categories: list[str],
    excluded_subjects: list[str],
    current_user: dict = Depends(get_current_active_user),
):
    """
    Update the user's schedule exclusion filters.
    """
    with db.session() as session:
        service = ScheduleService(session)
        return service.update_filters(
            current_user["id"],
            excluded_categories,
            excluded_subjects,
        )


@router.get("", include_in_schema=True)
@router.get("/", include_in_schema=False)
def get_today_schedule(
    current_user: dict = Depends(get_current_active_user),
):
    """
    Get today's schedule for the current user.
    """
    with db.session() as session:
        service = ScheduleService(session)
        return service.get_today_schedule(current_user["id"])
