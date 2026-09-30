"""
Test suite for verifying Focus evidence functionality
Tests Phase 5 runtime behavior
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.database.db import Database
from app.database.models import User, FocusSession, FocusEvidence, Lesson
from app.focus.service import FocusService


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


class TestFocusEvidence:
    """Test focus evidence functionality"""

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

    def test_valid_text_evidence_accepted(self, session, test_user, test_lesson):
        """Test that valid text evidence is accepted"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act: Add valid text evidence
        evidence = {
            "type": "text",
            "content": "This is valid text evidence for the goal"
        }

        # This should not raise an exception
        focus_evidence = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence
        )

        # Assert
        assert focus_evidence is not None
        assert focus_evidence.type == "text"
        assert focus_evidence.content == "This is valid text evidence for the goal"
        assert focus_evidence.file_path is None
        assert focus_evidence.focus_session_id == session_obj.id

        # Check that evidence_provided flag is set on the session
        updated_session = focus_service.get_session(session_id=session_obj.id, user_id=user_id)
        assert updated_session.evidence_provided == True

    def test_valid_url_evidence_accepted(self, session, test_user, test_lesson):
        """Test that valid URL evidence is accepted"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act: Add valid URL evidence
        evidence = {
            "type": "url",
            "content": "https://example.com/evidence"
        }

        # This should not raise an exception
        focus_evidence = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence
        )

        # Assert
        assert focus_evidence is not None
        assert focus_evidence.type == "url"
        assert focus_evidence.content == "https://example.com/evidence"
        assert focus_evidence.file_path is None
        assert focus_evidence.focus_session_id == session_obj.id

    def test_valid_image_evidence_accepted(self, session, test_user, test_lesson):
        """Test that valid image evidence is accepted"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act: Add valid image evidence
        evidence = {
            "type": "image",
            "content": "base64encodedimageordescription"
        }

        # This should not raise an exception
        focus_evidence = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence
        )

        # Assert
        assert focus_evidence is not None
        assert focus_evidence.type == "image"
        assert focus_evidence.content == "base64encodedimageordescription"
        assert focus_evidence.file_path is None
        assert focus_evidence.focus_session_id == session_obj.id

    def test_valid_file_evidence_accepted(self, session, test_user, test_lesson):
        """Test that valid file evidence is accepted"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act: Add valid file evidence
        evidence = {
            "type": "file",
            "content": "file content description",
            "file_path": "/path/to/file.pdf"
        }

        # This should not raise an exception
        focus_evidence = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence
        )

        # Assert
        assert focus_evidence is not None
        assert focus_evidence.type == "file"
        assert focus_evidence.content == "file content description"
        assert focus_evidence.file_path == "/path/to/file.pdf"
        assert focus_evidence.focus_session_id == session_obj.id

    def test_empty_evidence_content_rejected(self, session, test_user, test_lesson):
        """Test that empty evidence content is rejected"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act & Assert: Add evidence with empty content
        evidence = {
            "type": "text",
            "content": ""  # Empty content
        }

        with pytest.raises(ValueError, match="Evidence content must be a non-empty string"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence
            )

    def test_whitespace_only_evidence_content_rejected(self, session, test_user, test_lesson):
        """Test that whitespace-only evidence content is rejected"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act & Assert: Add evidence with whitespace-only content
        evidence = {
            "type": "text",
            "content": "   \t\n  "  # Whitespace only
        }

        with pytest.raises(ValueError, match="Evidence content must be a non-empty string"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence
            )

    def test_invalid_evidence_type_rejected(self, session, test_user, test_lesson):
        """Test that invalid evidence type is rejected"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act & Assert: Add evidence with invalid type
        evidence = {
            "type": "invalid_type",
            "content": "Some content"
        }

        with pytest.raises(ValueError, match="Invalid evidence type: invalid_type"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence
            )

    def test_malformed_url_evidence_rejected(self, session, test_user, test_lesson):
        """Test that malformed URL evidence is rejected"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act & Assert: Add evidence with malformed URL
        evidence = {
            "type": "url",
            "content": "not-a-valid-url"
        }

        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence
            )

        # Test another malformed URL
        evidence2 = {
            "type": "url",
            "content": "ftp://example.com/file"
        }

        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence2
            )

    def test_evidence_attached_to_correct_session(self, session, test_user, test_lesson):
        """Test that evidence is attached to the correct session"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start first focus session
        session1 = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal 1"
        )

        # Act: Add evidence to session1
        evidence = {
            "type": "text",
            "content": "Evidence for session 1"
        }

        focus_evidence = focus_service.add_evidence(
            session_id=session1.id,
            user_id=user_id,
            evidence=evidence
        )

        # Complete the first session so it's no longer active
        focus_service.complete_focus_session(
            session_id=session1.id,
            user_id=user_id,
            completion_mode="manual"
        )

        # Start second focus session (should be a new session since first is completed)
        session2 = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal 2"
        )

        # Assert
        assert focus_evidence.focus_session_id == session1.id
        assert focus_evidence.focus_session_id != session2.id

        # Check that only session1 has evidence_provided set
        updated_session1 = focus_service.get_session(session_id=session1.id, user_id=user_id)
        updated_session2 = focus_service.get_session(session_id=session2.id, user_id=user_id)
        assert updated_session1.evidence_provided == True
        assert updated_session2.evidence_provided == False

    def test_evidence_from_other_users_session_rejected(self, session, test_user, test_lesson):
        """Test that evidence cannot be added to another user's session"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Create another user
        other_user = User(
            email=f"other_{uuid4()}@example.com",
            name="Other User",
            password_hash="hashed_password",
            is_active=1,
            onboarding_completed=1,
            email_verified=1,
        )
        session.add(other_user)
        session.commit()
        session.refresh(other_user)

        # Start a focus session for the other user
        other_session = focus_service.start_focus_session(
            user_id=other_user.id,
            goal_text="Other user's goal"
        )

        # Act & Assert: Try to add evidence to other user's session as test user
        evidence = {
            "type": "text",
            "content": "Unauthorized evidence"
        }

        with pytest.raises(ValueError, match="Focus session not found"):
            focus_service.add_evidence(
                session_id=other_session.id,
                user_id=user_id,  # Trying to access other user's session
                evidence=evidence
            )

    def test_multiple_evidence_per_session_allowed(self, session, test_user, test_lesson):
        """Test that multiple evidence can be attached to the same session"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Act: Add multiple evidence items
        evidence1 = {
            "type": "text",
            "content": "First piece of evidence"
        }

        evidence2 = {
            "type": "url",
            "content": "https://example.com/second-evidence"
        }

        evidence3 = {
            "type": "image",
            "content": "Description of third evidence"
        }

        focus_evidence1 = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence1
        )

        focus_evidence2 = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence2
        )

        focus_evidence3 = focus_service.add_evidence(
            session_id=session_obj.id,
            user_id=user_id,
            evidence=evidence3
        )

        # Assert
        assert focus_evidence1 is not None
        assert focus_evidence2 is not None
        assert focus_evidence3 is not None
        assert focus_evidence1.id != focus_evidence2.id
        assert focus_evidence2.id != focus_evidence3.id
        assert focus_evidence1.id != focus_evidence3.id

        # Check that all evidence is linked to the same session
        assert focus_evidence1.focus_session_id == session_obj.id
        assert focus_evidence2.focus_session_id == session_obj.id
        assert focus_evidence3.focus_session_id == session_obj.id

        # Check evidence count
        evidences = focus_service.get_evidence_for_session(session_obj.id)
        assert len(evidences) == 3

    def test_evidence_cannot_be_added_to_completed_session(self, session, test_user, test_lesson):
        """Test that evidence cannot be added to a completed session"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start and complete a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        completed_session = focus_service.complete_focus_session(
            session_id=session_obj.id,
            user_id=user_id,
            completion_mode="manual"
        )

        # Act & Assert: Try to add evidence to completed session
        evidence = {
            "type": "text",
            "content": "Evidence after completion"
        }

        with pytest.raises(ValueError, match="Cannot add evidence to a session that is not active or paused"):
            focus_service.add_evidence(
                session_id=completed_session.id,
                user_id=user_id,
                evidence=evidence
            )

    def test_evidence_cannot_be_added_to_cancelled_session(self, session, test_user, test_lesson):
        """Test that evidence cannot be added to a cancelled session"""
        # Arrange
        focus_service = FocusService(session)
        user_id = test_user.id

        # Start a focus session
        session_obj = focus_service.start_focus_session(
            user_id=user_id,
            goal_text="Test goal"
        )

        # Manually set session to cancelled (simulating cancellation)
        session_obj.status = "cancelled"
        session.commit()

        # Act & Assert: Try to add evidence to cancelled session
        evidence = {
            "type": "text",
            "content": "Evidence after cancellation"
        }

        with pytest.raises(ValueError, match="Cannot add evidence to a session that is not active or paused"):
            focus_service.add_evidence(
                session_id=session_obj.id,
                user_id=user_id,
                evidence=evidence
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])