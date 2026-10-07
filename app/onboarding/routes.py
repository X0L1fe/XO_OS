from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from app.auth.service import get_current_active_user
from app.database.models import User
from app.database.db import db

router = APIRouter()


@router.post("/onboarding/complete")
async def complete_onboarding(
    request: Request, current_user: User = Depends(get_current_active_user)
):
    """Complete onboarding by saving group and calendar selection."""
    try:
        data = await request.json()
        group_name = data.get("group_name")
        calendar_id = data.get("calendar_id", "primary")

        if not group_name:
            raise HTTPException(status_code=400, detail="Group name is required")

        with db.session() as session:
            user = session.query(User).filter(User.id == current_user.id).one()
            user.mais_group_id = group_name
            user.selected_calendar_id = calendar_id
            user.onboarding_completed = True
            session.commit()
        return {"status": "success"}
    except Exception as e:
        # Log the error for debugging
        print(f"Error in complete_onboarding: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to complete onboarding: {str(e)}"
        )