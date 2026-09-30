"""
Test suite for verifying Focus completion and AI verification functionality
Tests Phases 4-8 runtime behavior
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.database.db import Database
from app.database.models import User, UserStats, FocusSession, FocusEvidence, Lesson, ScheduleExclusion, XPTransaction
from app.focus.service import FocusService
from app.ai.verification import AIVerificationService, VerificationResult
from app.event import publish_focus_updated, publish_gamification_updated


def create_test_user(db_session):
    """Helper to create a test user"""
    user = User(
        email=f"test_{uuid4()}@example.com",
        name="Test User",
        password_hash="hashed_password",
        is_active=1,
        onboarding_completed=1,
        email_verified=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_test_lesson(db_session, user_id):
    """Helper to create a test lesson"""
    now = datetime.now(timezone.utc)
    lesson = Lesson(
        user_id=user_id,
        subject="Test Subject",
        lesson_type="LECTURE",
        category="REGULAR",
        start_time=now - timedelta(hours=1),
        end_time=now + timedelta(hours=1),
        content_hash="test_hash",
        stable_id="test-stable-id",
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    return lesson


class TestFocusCompletion:
    """Test focus completion functionality"""

    @pytest.fixture
    def db(self):
        """Create an in-memory SQLite database for testing"""
        db = Database("sqlite:///:memory:")
        yield db

    @pytest.fixture
    def session(self, db):
        """Create a database session"""
        with db.session() as session:
            yield session

    @pytest.fixture
    def test_user(self, session):
        """Create a test user"""
        return create_test_user(session)

    @pytest.fixture
    def test_lesson(self, session, test_user):
        """Create a test lesson"""
        return create_test_lesson(session, test_user.id)

    def create_test_focus_session(self, session, user_id, lesson_id):
        """Helper to create a focus session in the database"""
        now = datetime.now(timezone.utc)
        focus_session = FocusSession(
            user_id=user_id,
            lesson_id=lesson_id,
            goal_text="Test goal",
            status="active",
            started_at=now,
        )
        session.add(focus_session)
        session.commit()
        session.refresh(focus_session)
        return focus_session

    def test_manual_completion_awards_3_xp(self, session, test_user, test_lesson):
        """Test that manual completion awards exactly 3 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)

        # Complete manually
        completed_session = focus_service.complete_focus_session(
            session_id=session_obj.id,
            user_id=user_id,
            completion_mode="manual"
        )

        # Assert
        assert completed_session.status == "completed"
        assert completed_session.completion_mode == "manual"
        assert completed_session.verification_status == "not_required"
        assert completed_session.xp_awarded == 3

        # Check XP transaction was created
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1
        assert xp_transactions[0].amount == 3
        assert xp_transactions[0].reason == "focus_completed"
        assert xp_transactions[0].source_type == "focus_session"
        assert xp_transactions[0].source_id == completed_session.id

        # Check UserStats updated
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats.total_xp == 3
        assert stats.level == 1  # 3 XP is less than 1000 needed for level 2

    def test_manual_completion_no_duplicate_xp(self, session, test_user, test_lesson):
        """Test that manual completion doesn't award XP twice"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)

        # First completion
        focus_service.complete_focus_session(
            session_id=session_obj.id,
            user_id=user_id,
            completion_mode="manual"
        )

        # Assert first completion
        xp_transactions_after_first = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions_after_first) == 1

        stats_after_first = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats_after_first.total_xp == 3

        # Act: Try to complete again (should not award additional XP)
        # Note: The second completion will fail because the session is already completed
        # but we're testing that no additional XP is awarded

        # Actually, let's test idempotency by trying to process AI verification on a completed session
        # For manual completion, we need to test that calling complete_focus_session again on same session fails
        # but doesn't award more XP - this is handled by the validation in complete_focus_session

        # Try to complete the same session again - should raise ValueError
        with pytest.raises(ValueError, match="Focus session not found or not in a completable state"):
            focus_service.complete_focus_session(
                session_id=session_obj.id,
                user_id=user_id,
                completion_mode="manual"
            )

        # Assert no additional XP was awarded
        xp_transactions_after_second = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions_after_second) == 1  # Still only one

        stats_after_second = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats_after_second.total_xp == 3  # Still only 3 XP

    def test_ai_verified_approved_score_0_awards_10_xp(self, session, test_user, test_lesson):
        """Test that AI verified completion with score 0.0 awards 10 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session and set it to completed with ai_verified mode
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)
        # We need to set it to completed status and ai_verified mode manually for the test
        # because we want to test the verification processing directly
        session_obj.status = "completed"
        session_obj.completion_mode = "ai_verified"
        session_obj.verification_status = "pending"
        session.commit()
        session.refresh(session_obj)

        # Simulate AI verification result with score 0.0
        verification_result = VerificationResult(
            approved=True,
            confidence=0.8,
            score=0.0,
            reason="Goal met",
            missing=[]
        )

        # Act: Process the verification result
        focus_service.process_ai_verification_result(
            user_id=user_id,
            verification_result=verification_result,
            session=session_obj
        )

        # Assert
        assert session_obj.verification_status == "approved"
        assert session_obj.xp_awarded == 10  # 10 base + 0 bonus

        # Check XP transaction
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1
        assert xp_transactions[0].amount == 10
        assert xp_transactions[0].reason == "focus_verified"
        assert xp_transactions[0].source_type == "focus_session"
        assert xp_transactions[0].source_id == session_obj.id

        # Check UserStats
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats.total_xp == 10

    def test_ai_verified_approved_score_0_5_awards_15_xp(self, session, test_user, test_lesson):
        """Test that AI verified completion with score 0.5 awards 15 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session and set it to completed with ai_verified mode
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)
        session_obj.status = "completed"
        session_obj.completion_mode = "ai_verified"
        session_obj.verification_status = "pending"
        session.commit()
        session.refresh(session_obj)

        # Simulate AI verification result with score 0.5
        verification_result = VerificationResult(
            approved=True,
            confidence=0.7,
            score=0.5,
            reason="Goal mostly met",
            missing=["minor detail"]
        )

        # Act
        focus_service.process_ai_verification_result(
            user_id=user_id,
            verification_result=verification_result,
            session=session_obj
        )

        # Assert
        assert session_obj.verification_status == "approved"
        assert session_obj.xp_awarded == 15  # 10 base + 5 bonus

        # Check XP transaction
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1
        assert xp_transactions[0].amount == 15

        # Check UserStats
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats.total_xp == 15

    def test_ai_verified_approved_score_1_0_awards_20_xp(self, session, test_user, test_lesson):
        """Test that AI verified completion with score 1.0 awards 20 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session and set it to completed with ai_verified mode
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)
        session_obj.status = "completed"
        session_obj.completion_mode = "ai_verified"
        session_obj.verification_status = "pending"
        session.commit()
        session.refresh(session_obj)

        # Simulate AI verification result with score 1.0
        verification_result = VerificationResult(
            approved=True,
            confidence=0.9,
            score=1.0,
            reason="Goal perfectly met",
            missing=[]
        )

        # Act
        focus_service.process_ai_verification_result(
            user_id=user_id,
            verification_result=verification_result,
            session=session_obj
        )

        # Assert
        assert session_obj.verification_status == "approved"
        assert session_obj.xp_awarded == 20  # 10 base + 10 bonus

        # Check XP transaction
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1
        assert xp_transactions[0].amount == 20

        # Check UserStats
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        assert stats.total_xp == 20

    def test_ai_verified_rejected_awards_0_xp(self, session, test_user, test_lesson):
        """Test that AI verified completion when rejected awards 0 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session and set it to completed with ai_verified mode
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)
        session_obj.status = "completed"
        session_obj.completion_mode = "ai_verified"
        session_obj.verification_status = "pending"
        session.commit()
        session.refresh(session_obj)

        # Simulate AI verification result (rejected)
        verification_result = VerificationResult(
            approved=False,
            confidence=0.6,
            score=0.8,  # Score doesn't matter when rejected
            reason="Insufficient evidence",
            missing=["key component"]
        )

        # Act
        focus_service.process_ai_verification_result(
            user_id=user_id,
            verification_result=verification_result,
            session=session_obj
        )

        # Assert
        assert session_obj.verification_status == "rejected"
        assert session_obj.xp_awarded == 0

        # Check no XP transaction was created
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 0

        # Check UserStats unchanged (if no stats row, treat total_xp as 0)
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        total_xp = stats.total_xp if stats else 0
        assert total_xp == 0

    def test_ai_verified_error_awards_0_xp(self, session, test_user, test_lesson):
        """Test that AI verified completion when error awards 0 XP"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session and set it to completed with ai_verified mode
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)
        session_obj.status = "completed"
        session_obj.completion_mode = "ai_verified"
        session_obj.verification_status = "pending"
        session.commit()
        session.refresh(session_obj)

        # Simulate AI verification result (technical error)
        verification_result = VerificationResult(
            approved=False,
            confidence=0.0,
            score=0.0,
            reason="Failed to parse AI response",
            missing=[]
        )

        # Act
        focus_service.process_ai_verification_result(
            user_id=user_id,
            verification_result=verification_result,
            session=session_obj
        )

        # Assert
        assert session_obj.verification_status == "error"
        assert session_obj.xp_awarded == 0

        # Check no XP transaction was created
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 0

        # Check UserStats unchanged (if no stats row, treat total_xp as 0)
        stats = session.query(UserStats).filter(UserStats.user_id == user_id).first()
        total_xp = stats.total_xp if stats else 0
        assert total_xp == 0


def test_manual_completion_race_condition(self, session, test_user, test_lesson):
        """Test that concurrent manual completions of the same session do not award XP twice"""
        import threading

        focus_service = FocusService(session)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session
        session_obj = self.create_test_focus_session(session, user_id, lesson_id)

        # We'll store the results from each thread
        results = []

        def complete_session():
            try:
                completed_session = focus_service.complete_focus_session(
                    session_id=session_obj.id,
                    user_id=user_id,
                    completion_mode="manual"
                )
                results.append(("success", completed_session.id))
            except Exception as e:
                results.append(("error", str(e)))

        # Create two threads
        thread1 = threading.Thread(target=complete_session)
        thread2 = threading.Thread(target=complete_session)

        # Start both threads
        thread1.start()
        thread2.start()

        # Wait for both threads to complete
        thread1.join()
        thread2.join()

        # We expect one success and one error (because the second will see the session is no longer active/paused)
        success_count = sum(1 for r in results if r[0] == "success")
        error_count = sum(1 for r in results if r[0] == "error")
        assert success_count == 1, f"Expected 1 success, got {success_count}"
        assert error_count == 1, f"Expected 1 error, got {error_count}"

        # Check that only one XP transaction was created
        xp_transactions = session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1, f"Expected 1 XP transaction, got {len(xp_transactions)}"
        assert xp_transactions[0].amount == 3, f"Expected 3 XP, got {xp_transactions[0].amount}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])