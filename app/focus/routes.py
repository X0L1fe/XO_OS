from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)

from app.ai.verification import (
    AIVerificationService,
    VerificationResult,
    get_ai_verification_service,
)
from app.auth.service import get_current_active_user, get_current_user
from app.database.db import db
from app.database.models import FocusSession, User
from app.event import publish_focus_updated, publish_gamification_updated
from app.focus.service import FocusService
from app.focus.storage import delete_evidence_image, save_evidence_image

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
    completion_mode: str = Body("manual", embed=True),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
):
    """
    Завершите фокус-сессию.
    Если для режима завершения выбрано значение «ручной», мы немедленно начисляем базовый опыт (3 опыта).
    Если для завершения_режима установлено значение «ai_verified», мы устанавливаем для проверки_статуса значение «ожидание» и начисляем XP после проверки.
    """
    with db.session() as session:
        focus_service = FocusService(session)

        try:
            # First, complete the session (this sets ended_at, etc.)
            session_obj = focus_service.complete_focus_session(
                session_id=session_id,
                user_id=current_user.id,
                completion_mode=completion_mode,
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
            ai_service = get_ai_verification_service()
            # Для проверки AI мы установили сеанс в режим ожидания проверки.
            # Нам нужно запустить проверку ИИ в фоновом режиме.
            if background_tasks is None:
                # Если нет фоновых задач, мы запустим их синхронно (не идеально, но для простоты)
                # В реальном приложении мы должны использовать фоновую задачу или очередь.
                # Перезагружаем доказательства из БД для этого сеанса
                evidence_objs = focus_service.get_evidence_for_session(session_obj.id)
                # Преобразование в список диктовок для службы AI
                evidence_list = [
                    {
                        "type": ev.type,
                        "content": ev.content,
                        "file_path": ev.file_path,
                    }
                    for ev in evidence_objs
                ]

                verification_result = await ai_service.verify_evidence(
                    goal=session_obj.goal_text or "",
                    evidence_list=evidence_list,
                )
                focus_service.process_ai_verification_result(
                    current_user.id, verification_result, session_obj
                )
                # Publish focus updated event for the final state
                publish_focus_updated(current_user.id)
            else:
                # Add a background task to handle the AI verification and XP awarding
                background_tasks.add_task(
                    _process_ai_verification,
                    session_id=session_obj.id,
                    user_id=current_user.id,
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
    Подсчитайте продуктивные секунды, затраченные на фокус-сессию.

    Для активной сессии:
        прошедшее = сейчас - начало_в - всего_пауз_секунд

    Для приостановленного сеанса:
        истекшее = пауза_в - начатое_в - общее_паузу_секунд

    Для завершенного сеанса:
        прошедшее = окончание_в - начало_в - общее количество_пауз_секунд
    """
    started_at = session.started_at

    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=timezone.utc)
    else:
        started_at = started_at.astimezone(timezone.utc)

    if session.status == "paused" and session.paused_at:
        end_time = session.paused_at
    elif session.ended_at:
        end_time = session.ended_at
    else:
        end_time = datetime.now(timezone.utc)

    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)
    else:
        end_time = end_time.astimezone(timezone.utc)

    total_duration = (end_time - started_at).total_seconds()
    productive_duration = total_duration - session.total_paused_seconds

    return max(0, int(productive_duration))


async def _process_ai_verification(
    session_id: int,
    user_id: int,
):
    """
    Фоновая проверка evidence через AI и начисление XP.
    Все зависимости создаются внутри, привязанные к отдельной сессии БД,
    потому что сессия запроса к этому моменту уже закрыта.
    """
    from app.ai.verification import get_ai_verification_service
    from app.database.db import db as db_module

    db_session = db_module.SessionLocal()
    try:
        local_focus_service = FocusService(db_session)
        local_ai_service = get_ai_verification_service()

        session = (
            db_session.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
            )
            .with_for_update()
            .first()
        )
        if not session:
            logger.error(
                "Session %s not found for user %s during AI verification",
                session_id,
                user_id,
            )
            return

        evidence_objs = local_focus_service.get_evidence_for_session(session_id)
        evidence_list = [
            {
                "type": ev.type,
                "content": ev.content,
                "file_path": ev.file_path,
            }
            for ev in evidence_objs
        ]

        verification_result = await local_ai_service.verify_evidence(
            goal=session.goal_text or "",
            evidence_list=evidence_list,
        )
        logger.info(
            "AI verification result: approved=%s confidence=%.2f score=%.2f "
            "reason=%r missing=%r",
            verification_result.approved,
            verification_result.confidence,
            verification_result.score,
            verification_result.reason,
            verification_result.missing,
        )

        local_focus_service.process_ai_verification_result(
            user_id, verification_result, session
        )

        publish_focus_updated(user_id)

    except Exception as e:
        logger.exception("Error in AI verification background task: %s", e)
    finally:
        db_session.close()


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
    evidence_type: str = Form(..., alias="type"),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
):
    """
    Добавляет evidence к фокус-сессии.

    Принимает multipart/form-data:
      - text:  type=text,  content=<строка>
      - url:   type=url,   content=<http(s)://...>
      - image: type=image, file=<binary>, content=<опционально, оригинальное имя>
    """
    evidence: dict

    if evidence_type == "image":
        if file is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image evidence requires a 'file' upload",
            )
        raw_bytes = await file.read()
        try:
            file_path = save_evidence_image(
                user_id=current_user.id,
                raw_bytes=raw_bytes,
                filename=file.filename or "",
                content_type=file.content_type or "",
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        evidence = {
            "type": "image",
            "content": (content or file.filename or "image").strip(),
            "file_path": file_path,
        }

    elif evidence_type == "url":
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL evidence requires 'content'",
            )
        evidence = {"type": "url", "content": content, "file_path": None}

    elif evidence_type == "text":
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text evidence requires 'content'",
            )
        evidence = {"type": "text", "content": content, "file_path": None}

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported evidence type: {evidence_type}",
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
                "url": (
                    f"/static/media/{new_evidence.file_path}"
                    if new_evidence.file_path
                    else None
                ),
                "created_at": new_evidence.created_at,
            }
    except ValueError as e:
        # Если файл уже записан, но БД отказала — подчистим за собой
        if evidence_type == "image":
            delete_evidence_image(evidence["file_path"])
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
