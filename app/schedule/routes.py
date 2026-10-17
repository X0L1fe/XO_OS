import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
)
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.service import get_current_active_user
from app.database.db import db
from app.google_calendar.service import GoogleCalendarSyncService
from app.schedule.service import (
    GoogleCalendarConnection,
    ScheduleService,
    _resync_google_for_user,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ScheduleFiltersPayload(BaseModel):
    excluded_categories: list[str] = Field(default_factory=list)
    excluded_subjects: list[str] = Field(default_factory=list)


@router.get("/filters")
def get_schedule_filters(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the user's schedule exclusion filters.
    """
    with db.session() as session:
        service = ScheduleService(session)
        return service.get_filter_data(current_user.id)


@router.put("/filters", response_model=None)
async def update_schedule_filters(
    payload: ScheduleFiltersPayload,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
):
    with db.session() as session:
        service = ScheduleService(session)
        result = service.update_filters(
            user_id=current_user.id,
            excluded_categories=payload.excluded_categories,
            excluded_subjects=payload.excluded_subjects,
        )

    background_tasks.add_task(
        _resync_google_for_user,
        user_id=current_user.id,
    )

    return result


@router.get("", include_in_schema=True)
@router.get("/", include_in_schema=False)
def get_today_schedule(
    mode: str = Query(default="today", pattern="^(today|all)$"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get today's schedule for the current user.
    """
    with db.session() as session:
        service = ScheduleService(session)
        return service.get_today_schedule(current_user.id, mode=mode)
