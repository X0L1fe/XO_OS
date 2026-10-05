from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from app.ai.verification import VerificationResult

# Import shared schedule filter helpers
from app.common.schedule_filters import (
    get_schedule_exclusions,
    lesson_is_excluded_by_category,
    lesson_is_excluded_by_subject,
    lesson_is_visible,
    normalize_schedule_category,
)
from app.common.time import utc_now, msk_now_naive
from app.database.models import (
    FocusEvidence,
    FocusSession,
    Lesson,
    ScheduleExclusion,
    User,
    UserStats,
    XPTransaction,
)

# Import event publishing functions
from app.event import publish_focus_updated, publish_gamification_updated


class FocusService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def start_focus_session(
        self, user_id: int, goal_text: Optional[str] = None
    ) -> FocusSession:
        """
        Start a new focus session for the user.
        The backend determines the current lesson based on time and user's schedule exclusions.
        If there is already an active session, return it.
        """
        # Check for existing active session
        active_session = (
            self.db.query(FocusSession)
            .filter(FocusSession.user_id == user_id, FocusSession.status == "active")
            .first()
        )
        if active_session:
            return active_session

        # Determine the current lesson based on time and schedule exclusions
        current_lesson = self.get_current_lesson(user_id)

        # Create new focus session
        new_session = FocusSession(
            user_id=user_id,
            lesson_id=current_lesson.id if current_lesson else None,
            goal_text=goal_text,
            status="active",
            started_at=utc_now(),
        )
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return new_session

    def pause_focus_session(self, session_id: int, user_id: int) -> FocusSession:
        """
        Pause an active focus session.
        """
        session = (
            self.db.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
                FocusSession.status == "active",
            )
            .first()
        )
        if not session:
            raise ValueError("Active focus session not found")

        if session.paused_at is not None:
            # Already paused
            return session

        session.paused_at = utc_now()
        session.status = "paused"
        self.db.commit()
        self.db.refresh(session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return session

    def resume_focus_session(self, session_id: int, user_id: int) -> FocusSession:
        """
        Resume a paused focus session.
        """
        session = (
            self.db.query(FocusSession)
            .filter(
                FocusSession.id == session_id,
                FocusSession.user_id == user_id,
                FocusSession.status == "paused",
            )
            .first()
        )
        if not session:
            raise ValueError("Paused focus session not found")

        if session.paused_at is None:
            # Not paused
            return session

        # Calculate the paused duration and add to total_paused_seconds
        now = utc_now()
        # Ensure session.paused_at is offset-aware in UTC
        if session.paused_at.tzinfo is None:
            paused_at = session.paused_at.replace(tzinfo=timezone.utc)
        else:
            paused_at = session.paused_at.astimezone(timezone.utc)
        paused_duration = (now - paused_at).total_seconds()
        session.total_paused_seconds += int(paused_duration)
        session.paused_at = None
        session.status = "active"
        self.db.commit()
        self.db.refresh(session)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return session

    def complete_focus_session(
        self,
        session_id: int,
        user_id: int,
        completion_mode: str = "manual",
        evidence: Optional[List[dict]] = None,
    ) -> FocusSession:
        """
        Завершите фокус-сессию.
        Если для завершения_режима установлено значение "manual", мы начисляем базовый опыт и устанавливаем для параметра_статуса_проверки значение "not_required".
        Если для завершения_режима установлено значение «ai_verified», мы запускаем процесс проверки ИИ (асинхронный) и устанавливаем для verification_status  значение "pending".
        Фактическое начисление опыта за проверку ИИ произойдет после завершения проверки.
        """
        session_query = self.db.query(FocusSession).filter(
            FocusSession.id == session_id,
            FocusSession.user_id == user_id,
            FocusSession.status.in_(["active", "paused"]),
        )
        session_query = session_query.with_for_update()
        session = session_query.first()

        if not session:
            raise ValueError("Focus session not found or not in a completable state")

        # Check if we have already rewarded XP for this lesson occurrence
        # This prevents farming XP by creating multiple focus sessions for the same lesson
        if session.lesson_id:
            existing_rewarded_session = (
                self.db.query(FocusSession)
                .filter(
                    FocusSession.user_id == user_id,
                    FocusSession.lesson_id == session.lesson_id,
                    FocusSession.status == "completed",
                    FocusSession.xp_awarded > 0,
                    FocusSession.id != session_id,  # Exclude current session
                )
                .first()
            )
            if existing_rewarded_session:
                raise ValueError(
                    "XP has already been awarded for this lesson occurrence"
                )

        # Set ended_at and calculate duration
        now = utc_now()

        if session.status == "paused" and session.paused_at:
            paused_at = session.paused_at

            if paused_at.tzinfo is None:
                paused_at = paused_at.replace(tzinfo=timezone.utc)
            else:
                paused_at = paused_at.astimezone(timezone.utc)

            current_pause_duration = (now - paused_at).total_seconds()

            session.total_paused_seconds += int(current_pause_duration)
            session.paused_at = None

        session.ended_at = now

        # Ensure session.started_at is offset-aware in UTC
        if session.started_at.tzinfo is None:
            started_at = session.started_at.replace(tzinfo=timezone.utc)
        else:
            started_at = session.started_at.astimezone(timezone.utc)

        # Calculate total duration and productive duration (excluding pauses)
        total_duration = (session.ended_at - started_at).total_seconds()
        productive_duration = total_duration - session.total_paused_seconds
        session.duration_seconds = max(0, int(productive_duration))

        session.completion_mode = completion_mode
        session.status = "completed"

        if completion_mode == "manual":
            # Manual completion: award base XP (e.g., 3 XP)
            base_xp = 3
            session.xp_awarded = base_xp
            session.verification_status = "not_required"
            # Award the XP immediately
            self._award_xp(user_id, base_xp, "focus_completed", session.id)
        elif completion_mode == "ai_verified":
            # AI verified: we don't award XP yet, we set verification_status to pending and will award after verification
            session.verification_status = "pending"
            # We do not commit the session yet because we want to wait for the AI verification result?
            # Actually, we can commit the session with pending status and then update it after verification.
            # But note: the user wants the completion to be asynchronous, so we return the session in pending state.
            # We'll commit the session now with pending status, and then the AI verification will update it later.
            self.db.commit()
            self.db.refresh(session)
            # Publish focus updated event
            publish_focus_updated(user_id)
            # TODO: Trigger AI verification in the background (e.g., using a background task or a separate process)
            # For now, we'll just return the session and the caller (the API) can trigger the verification.
            # We'll leave the actual verification to the API layer.
            return session
        else:
            raise ValueError("Invalid completion mode")

        return session

    def _award_xp(
        self, user_id: int, amount: int, reason: str, source_id: Optional[int] = None
    ) -> None:
        """
        Наградите пользователя XP и обновите UserStats.
        Это вызывается, когда необходимо начислить XP (например, после завершения вручную или после одобрения проверки ИИ).
        """
        # Создать транзакцию XP
        xp_transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            reason=reason,
            source_type="focus_session",
            source_id=source_id,
        )
        self.db.add(xp_transaction)

        # Обновление UserStats
        stats = self.db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id, total_xp=0, level=1, max_streak=0)
            self.db.add(stats)

        stats.total_xp += amount
        # Обновление уровня: каждые 1000 XP = 1 level
        new_level = (stats.total_xp // 1000) + 1
        if new_level > stats.level:
            stats.level = new_level

        # Обновление серии: мы учитываем сегодняшнюю дату серии
        today = utc_now().date()
        if stats.last_activity_date:
            last_activity_date = stats.last_activity_date.date()
            if today == last_activity_date:
                # В тот же день, серия остается прежней (мы увеличиваем только один раз в день)
                pass
            elif today == last_activity_date + timedelta(days=1):
                # Последующий день
                stats.current_streak += 1
            else:
                # Разрыв в днях, полоса сбросов
                stats.current_streak = 1
        else:
            # Первое действие
            stats.current_streak = 1

        # При необходимости обновите максимальную серию
        if stats.current_streak > stats.max_streak:
            stats.max_streak = stats.current_streak

        stats.last_activity_date = datetime.now(timezone.utc)
        self.db.commit()

        # Опубликовать обновленное событие геймификации
        publish_gamification_updated(user_id)

    def get_active_session(self, user_id: int) -> Optional[FocusSession]:
        """
        Получите сеанс активного фокуса для пользователя, если таковой имеется.
        """
        return (
            self.db.query(FocusSession)
            .filter(FocusSession.user_id == user_id, FocusSession.status == "active")
            .first()
        )

    def get_current_session(self, user_id: int) -> Optional[FocusSession]:
        """
        Получите текущий незавершенный сеанс фокусировки для пользователя.

        Текущая сессия может быть активной или приостановленной.
        Завершенные сессии не возвращаются.
        """
        return (
            self.db.query(FocusSession)
            .filter(
                FocusSession.user_id == user_id,
                FocusSession.status.in_(["active", "paused"]),
            )
            .order_by(FocusSession.id.desc())
            .first()
        )

    def get_session(
        self, session_id: int, user_id: int, for_update: bool = False
    ) -> Optional[FocusSession]:
        """
        Получите сеанс фокусировки по идентификатору, гарантируя, что он принадлежит пользователю.
        """
        query = self.db.query(FocusSession).filter(
            FocusSession.id == session_id, FocusSession.user_id == user_id
        )
        if for_update:
            query = query.with_for_update()
        return query.first()

    def get_evidence_for_session(self, session_id: int) -> List[FocusEvidence]:
        """
        Получите все доказательства для фокус-сессии.
        """
        return (
            self.db.query(FocusEvidence)
            .filter(FocusEvidence.focus_session_id == session_id)
            .order_by(FocusEvidence.id)
            .all()
        )

    def get_current_lesson(self, user_id: int) -> Optional[Lesson]:
        """
        Получите текущий видимый урок для пользователя на основе текущего времени и исключений расписания.
        Бэкенд определяет текущий урок — не доверяет входным данным фронтенда.
        """
        now = msk_now_naive()

        # Get user's schedule exclusions
        excluded_categories, excluded_subjects = self._get_schedule_exclusions(user_id)

        # Find lessons that are currently happening
        lessons = (
            self.db.query(Lesson)
            .filter(
                Lesson.user_id == user_id,
                Lesson.start_time <= now,
                Lesson.end_time >= now,
            )
            .order_by(Lesson.start_time)
            .all()
        )

        # Return the first visible lesson
        lesson = next(
            (
                item
                for item in lessons
                if lesson_is_visible(
                    item,
                    excluded_categories,
                    excluded_subjects,
                )
            ),
            None,
        )
        return lesson

    def _get_schedule_exclusions(self, user_id: int) -> tuple[set, set]:
        """
        Get the user's schedule exclusions as sets of normalized category and subject values.
        Returns (excluded_categories, excluded_subjects).
        """
        return get_schedule_exclusions(self.db, user_id)

    def _validate_and_prepare_evidence(
        self, evidence: dict
    ) -> tuple[str, str, Optional[str]]:
        """
        Проверка и подготовка доказательств к хранению.
        Возвращает кортеж (тип, содержимое, путь к файлу).
        Вызывает ValueError, если свидетельство недействительно.
        """
        if not isinstance(evidence, dict):
            raise ValueError("Evidence must be a dictionary")

        evidence_type = evidence.get("type")
        if evidence_type not in ["text", "url", "image"]:
            raise ValueError(
                f"Invalid evidence type: {evidence_type}. Must be one of: text, url, image"
            )

        content = evidence.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Evidence content must be a non-empty string")

        file_path = None  # инициализируем заранее

        if evidence_type == "url":
            if not (content.startswith("http://") or content.startswith("https://")):
                raise ValueError("URL must start with http:// or https://")
        elif evidence_type == "image":
            file_path = evidence.get("file_path")
            if not file_path or not isinstance(file_path, str):
                raise ValueError(
                    "file_path is required and must be a non-empty string for image evidence"
                )

        return evidence_type, content.strip(), file_path

    def add_evidence(
        self, session_id: int, user_id: int, evidence: dict
    ) -> FocusEvidence:
        """
        Add evidence to a focus session.
        """
        session = self.get_session(session_id, user_id)
        if not session:
            raise ValueError("Focus session not found")
        if session.status not in ["active", "paused"]:
            raise ValueError(
                "Cannot add evidence to a session that is not active or paused"
            )

        evidence_type, content, file_path = self._validate_and_prepare_evidence(
            evidence
        )
        new_evidence = FocusEvidence(
            focus_session_id=session.id,
            type=evidence_type,
            content=content,
            file_path=file_path,
        )
        self.db.add(new_evidence)
        session.evidence_provided = True
        self.db.commit()
        self.db.refresh(new_evidence)

        # Publish focus updated event
        publish_focus_updated(user_id)

        return new_evidence

    def process_ai_verification_result(
        self,
        user_id: int,
        verification_result: VerificationResult,
        session: FocusSession,
    ) -> None:
        """
        Обработайте результат проверки ИИ и соответствующим образом начислите XP.
        Этот метод централизует начисление XP за проверку ИИ на уровне обслуживания.
        """
        # Idempotency: if session is already in a final state, do nothing
        if session.verification_status != "pending":
            return

        # Persist the model's explanation for diagnostics / UI
        session.verification_reason = verification_result.reason
        session.verification_missing = json.dumps(
            verification_result.missing, ensure_ascii=False
        )

        # Define technical error reason indicators
        error_indicators = [
            "Failed to parse AI response",
            "Empty response from AI",
            "AI verification error",
            "No JSON found in AI response",
            "Invalid AI response fields",
            "Goal or evidence is missing",
        ]

        is_technical_error = any(
            verification_result.reason.startswith(indicator)
            for indicator in error_indicators
        )

        if is_technical_error:
            session.verification_status = "error"
            self.db.commit()
            return

        if verification_result.approved:
            # Успешная проверка -> одобрено, начисляется XP в зависимости от результата.
            session.verification_status = "approved"
            # Награждайте XP в зависимости от очков (базовая 10 + бонус до 10)
            base_xp = 10
            bonus_xp = int(verification_result.score * 10)  # 0-10
            total_xp = base_xp + bonus_xp
            session.xp_awarded = total_xp
            # Награжает XP внутренним методом.
            self._award_xp(user_id, total_xp, "focus_verified", session.id)
        else:
            # AI rejected evidence -> rejected, no XP
            session.verification_status = "rejected"
            self.db.commit()
            return