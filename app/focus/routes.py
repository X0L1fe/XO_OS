from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, status

from app.auth.service import get_current_user, get_current_active_user
from app.database.db import db
from app.database.models import User
from app.focus.service import FocusService
from app.ai.verification import AIVerificationService, get_ai_verification_service
from app.event import publish_focus_updated, publish_gamification_updated

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["focus"],
)


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_focus_session(
    goal_text: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
):
    """
    Start a new focus session for the current user.
    The backend determines the current lesson based on time and user's schedule.
    If there is already an active session, return it.
    """
    with db.session() as session:
        focus_service = FocusService(session)
        session_obj = focus_service.start_focus_session(
            user_id=current_user.id,
            goal_text=goal_text,
        )
        return {
            "session_id": session_obj.id,
            "status": session_obj.status,
            "lesson_id": session_obj.lesson_id,
            "lesson_subject": session_obj.lesson.subject if session_obj.lesson else "",
            "lesson_description": session_obj.lesson.description
            if session_obj.lesson
            else "",
            "goal_text": session_obj.goal_text,
            "started_at": session_obj.started_at,
            "elapsed_seconds": 0,  # Just started
            "xp_preview": 3
            if session_obj.completion_mode == "manual"
            else 10,  # Preview: manual gives 3, AI gives 10 base
        }


@router.post("/{session_id}/pause", status_code=status.HTTP_200_OK)
async def pause_focus_session(
    session_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
):
    """
    Pause an active focus session.
    """
    try:
        with db.session() as session:
            focus_service = FocusService(session)
            session_obj = focus_service.pause_focus_session(
                session_id=session_id,
                user_id=current_user.id,
            )
            return {
                "session_id": session_obj.id,
                "status": session_obj.status,
                "elapsed_seconds": _calculate_elapsed_seconds(session_obj),
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/resume", status_code=status.HTTP_200_OK)
async def resume_focus_session(
    session_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
):
    """
    Resume a paused focus session.
    """
    try:
        with db.session() as session:
            focus_service = FocusService(session)
            session_obj = focus_service.resume_focus_session(
                session_id=session_id,
                user_id=current_user.id,
            )
            return {
                "session_id": session_obj.id,
                "status": session_obj.status,
                "elapsed_seconds": _calculate_elapsed_seconds(session_obj),
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{session_id}/complete", status_code=status.HTTP_200_OK)
async def complete_focus_session(
    session_id: int = Path(..., gt=0),
    completion_mode: str = "manual",
    evidence: Optional[List[dict]] = None,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
):
    """
    Complete a focus session.
    If completion_mode is "manual", we award base XP (3 XP) immediately.
    If completion_mode is "ai_verified", we set verification_status to pending and award XP after verification.
    """
    with db.session() as session:
        focus_service = FocusService(session)
        ai_service = get_ai_verification_service()
        try:
            # First, complete the session (this sets ended_at, etc.)
            session_obj = focus_service.complete_focus_session(
                session_id=session_id,
                user_id=current_user.id,
                completion_mode=completion_mode,
                evidence=evidence,
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        if completion_mode == "manual":
            # For manual completion, the XP has already been awarded in the service.
            # We just need to return the updated session.
            return {
                "session_id": session_obj.id,
                "status": session_obj.status,
                "duration_seconds": session_obj.duration_seconds,
                "xp_awarded": session_obj.xp_awarded,
                "verification_status": session_obj.verification_status,
                "completion_mode": session_obj.completion_mode,
            }

        elif completion_mode == "ai_verified":
            # For AI verification, we have set the session to pending verification.
            # We need to trigger the AI verification in the background.
            if background_tasks is None:
                # If no background tasks, we'll run it synchronously (not ideal, but for simplicity)
                # In a real app, we should use a background task or a queue.
                verification_result = await ai_service.verify_evidence(
                    goal=session_obj.goal_text or "",
                    evidence=evidence or [],
                )
                # Update the session with the verification result
                session_obj.verification_status = (
                    "approved" if verification_result.approved else "rejected"
                )
                # If approved, award base XP (10) plus bonus based on score
                base_xp = 10
                bonus_xp = int(verification_result.score * 10)  # 0-10 bonus
                total_xp = base_xp + bonus_xp
                session_obj.xp_awarded = total_xp
                # Award the XP
                focus_service._award_xp(
                    user_id=current_user.id,
                    amount=total_xp,
                    reason="focus_verified",
                    source_id=session_obj.id,
                )
                # Update the session in the database
                session.commit()
                session.refresh(session_obj)
            else:
                # Add a background task to handle the AI verification and XP awarding
                background_tasks.add_task(
                    _process_ai_verification,
                    session_id=session_obj.id,
                    user_id=current_user.id,
                    goal=session_obj.goal_text or "",
                    evidence=evidence or [],
                    focus_service=focus_service,
                    ai_service=ai_service,
                )

            return {
                "session_id": session_obj.id,
                "status": session_obj.status,
                "duration_seconds": session_obj.duration_seconds,
                "verification_status": session_obj.verification_status,  # Will be "pending"
                "completion_mode": session_obj.completion_mode,
                "xp_preview": 10,  # Base XP for AI verification, bonus to be determined
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid completion mode",
            )


def _calculate_elapsed_seconds(session) -> int:
    """
    Calculate the elapsed seconds for a session, accounting for pauses.
    """
    if not session.ended_at:
        # Still active or paused
        end_time = datetime.now(timezone.utc)
    else:
        end_time = session.ended_at

    # Ensure both datetimes are offset-aware in UTC
    started_at = session.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    else:
        started_at = started_at.astimezone(timezone.utc)

    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    else:
        end_time = end_time.astimezone(timezone.utc)

    total_duration = (end_time - started_at).total_seconds()
    productive_duration = total_duration - session.total_paused_seconds
    return int(productive_duration)


async def _process_ai_verification(
    session_id: int,
    user_id: int,
    goal: str,
    evidence: list[dict],
    focus_service: FocusService,
    ai_service: AIVerificationService,
):
    """
    Background task to process AI verification and award XP.
    """
    # We need a new database session for the background task
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        # Re-create the services with the new db session
        local_focus_service = FocusService(db)
        local_ai_service = (
            ai_service  # The AI service doesn't hold db state, so we can reuse
        )

        # Verify the evidence
        verification_result = await local_ai_service.verify_evidence(
            goal=goal,
            evidence=evidence,
        )

        # Get the session
        session = local_focus_service.get_session(
            session_id=session_id, user_id=user_id
        )
        if not session:
            logger.error(
                f"Session {session_id} not found for user {user_id} during AI verification"
            )
            return

        # Update the session with the verification result
        if verification_result.approved:
            session.verification_status = "approved"
        else:
            session.verification_status = "rejected"

        # Calculate XP: base 10 + bonus up to 10 based on score
        base_xp = 10
        bonus_xp = int(verification_result.score * 10)  # 0-10
        total_xp = base_xp + bonus_xp
        session.xp_awarded = total_xp

        # Commit the session update
        db.commit()

        # Award the XP (this will update UserStats and emit events)
        local_focus_service._award_xp(
            user_id=user_id,
            amount=total_xp,
            reason="focus_verified",
            source_id=session.id,
        )

        # Publish focus updated event
        publish_focus_updated(user_id)

        # Note: The _award_xp method commits the transaction, so we don't need to commit again.
    except Exception as e:
        logger.error(f"Error in AI verification background task: {e}")
        # Optionally, we could update the session to an error state, but we'll leave it as pending for now.
    finally:
        db.close()


@router.get("/active", status_code=status.HTTP_200_OK)
async def get_active_focus_session(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the active focus session for the current user, if any.
    """
    with db.session() as session:
        focus_service = FocusService(session)
        session_obj = focus_service.get_active_session(user_id=current_user.id)
        if not session_obj:
            return None
        return {
            "session_id": session_obj.id,
            "status": session_obj.status,
            "lesson_id": session_obj.lesson_id,
            "goal_text": session_obj.goal_text,
            "started_at": session_obj.started_at,
            "elapsed_seconds": _calculate_elapsed_seconds(session_obj),
            "xp_preview": 3 if session_obj.completion_mode == "manual" else 10,
        }


@router.get("/{session_id}", status_code=status.HTTP_200_OK)
async def get_focus_session(
    session_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a focus session by ID.
    """
    with db.session() as session:
        focus_service = FocusService(session)
        session_obj = focus_service.get_session(
            session_id=session_id, user_id=current_user.id
        )
        if not session_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Focus session not found"
            )
        return {
            "session_id": session_obj.id,
            "status": session_obj.status,
            "lesson_id": session_obj.lesson_id,
            "goal_text": session_obj.goal_text,
            "started_at": session_obj.started_at,
            "ended_at": session_obj.ended_at,
            "duration_seconds": session_obj.duration_seconds,
            "total_paused_seconds": session_obj.total_paused_seconds,
            "completion_mode": session_obj.completion_mode,
            "verification_status": session_obj.verification_status,
            "xp_awarded": session_obj.xp_awarded,
            "evidence_provided": session_obj.evidence_provided,
        }


@router.post("/{session_id}/evidence", status_code=status.HTTP_200_OK)
async def add_evidence_to_focus_session(
    session_id: int = Path(..., gt=0),
    evidence: dict = None,
    current_user: User = Depends(get_current_user),
):
    """
    Add evidence to a focus session.
    """
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Evidence is required"
        )
    try:
        with db.session() as session:
            focus_service = FocusService(session)
            new_evidence = focus_service.add_evidence(
                session_id=session_id,
                user_id=current_user.id,
                evidence=evidence,
            )
            return {
                "id": new_evidence.id,
                "type": new_evidence.type,
                "content": new_evidence.content,
                "file_path": new_evidence.file_path,
                "created_at": new_evidence.created_at,
            }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
