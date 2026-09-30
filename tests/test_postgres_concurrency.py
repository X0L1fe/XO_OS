"""
PostgreSQL-based concurrency tests for Focus completion
Uses real PostgreSQL database to verify row-level locking
"""
import os
import pytest
import threading
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

# Set the database URL BEFORE importing any app modules
# Use psycopg2 driver to avoid libpq issues with psycopg 3.x
os.environ["XO_OS_DATABASE_URL"] = "postgresql+psycopg2://test:test@localhost:5432/test"

# Now import the app modules
from app.database.db import Database
from app.database.models import User, UserStats, FocusSession, FocusEvidence, Lesson, ScheduleExclusion, XPTransaction
from app.focus.service import FocusService
from app.ai.verification import AIVerificationService, VerificationResult
from sqlalchemy import select


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


def create_test_focus_session(db_session, user_id, lesson_id):
    """Helper to create a focus session in the database"""
    now = datetime.now(timezone.utc)
    focus_session = FocusSession(
        user_id=user_id,
        lesson_id=lesson_id,
        goal_text="Test goal",
        status="active",
        started_at=now,
    )
    db_session.add(focus_session)
    db_session.commit()
    db_session.refresh(focus_session)
    return focus_session


@pytest.fixture(scope="function")
def db():
    """Create a PostgreSQL database for testing"""
    # Use the database URL from environment (set above)
    db_instance = Database()
    yield db_instance
    # Clean up after test - close connections
    db_instance.engine.dispose()


def test_manual_completion_race_condition_postgres(db):
    """Test that concurrent manual completions of the same session do not award XP twice using PostgreSQL"""
    with db.session() as session:
        # Create test data within this session
        user = create_test_user(session)
        lesson = create_test_lesson(session, user.id)
        user_id = user.id
        lesson_id = lesson.id

        # Create a focus session in the database using a temporary session (so that it's committed and visible to other sessions)
        focus_session = create_test_focus_session(session, user_id, lesson_id)
        session_id = focus_session.id
        # Commit is done inside create_test_focus_session

    # We'll store the results from each thread
    results = []

    def complete_session():
        # Each thread creates its own session and focus service
        with db.session() as thread_session:
            thread_focus_service = FocusService(thread_session)
            try:
                # Check session state before attempting completion
                session_pre = thread_session.query(FocusSession).filter(
                    FocusSession.id == session_id
                ).first()
                if session_pre:
                    print(f"Thread {threading.get_ident()}: Session state before completion - status: {session_pre.status}, verification_status: {session_pre.verification_status}")
                else:
                    print(f"Thread {threading.get_ident()}: Session not found before completion attempt")

                completed_session = thread_focus_service.complete_focus_session(
                    session_id=session_id,
                    user_id=user_id,
                    completion_mode="manual"
                )
                results.append(("success", completed_session.id))
                print(f"Thread {threading.get_ident()}: Success - completed session {completed_session.id}, xp_awarded: {completed_session.xp_awarded}")
            except Exception as e:
                import traceback
                print(f"Exception in thread {threading.get_ident()}: {e}")  # Debug
                traceback.print_exc()
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

    print(f"Results: {results}")  # Debug

    # We expect one success and one error (because the second will see the session is no longer active/paused)
    success_count = sum(1 for r in results if r[0] == "success")
    error_count = sum(1 for r in results if r[0] == "error")
    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert error_count == 1, f"Expected 1 error, got {error_count}"

    # Check that only one XP transaction was created
    with db.session() as check_session:
        xp_transactions = check_session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1, f"Expected 1 XP transaction, got {len(xp_transactions)}"
        assert xp_transactions[0].amount == 3, f"Expected 3 XP, got {xp_transactions[0].amount}"


def test_ai_verification_race_condition_postgres(db):
    """Test that concurrent AI verification processing does not award XP twice using PostgreSQL"""
    print("!!!!!! TEST AI VERIFICATION RACE CONDITION POSTGRES STARTED !!!!!!")
    print(f"TEST STARTED: Using database URL: {os.environ.get('XO_OS_DATABASE_URL')}")
    with db.session() as session:
        # Create test data within this session
        user = create_test_user(session)
        lesson = create_test_lesson(session, user.id)
        user_id = user.id
        lesson_id = lesson.id

        # Create a focus session and set it to completed with ai_verified mode and pending verification
        focus_session = create_test_focus_session(session, user_id, lesson_id)
        # Manually set to completed and pending verification to simulate post-completion state
        focus_session.status = "completed"
        focus_session.completion_mode = "ai_verified"
        focus_session.verification_status = "pending"
        focus_session.goal_text = "Test goal"
        session.add(focus_session)
        session.commit()
        session.refresh(focus_session)
        session_id = focus_session.id
        print(f"Created focus session {session_id} for user {user_id}, lesson {lesson_id}")

    # We'll store the results from each thread
    results = []

    def process_verification():
        print(f"Thread {threading.get_ident()} starting: looking for session {session_id} for user {user_id}")
        # Each thread creates its own session and services
        with db.session() as thread_session:
            # We need to replicate the background task logic
            local_focus_service = FocusService(thread_session)
            local_ai_service = MagicMock(spec=AIVerificationService)
            # Mock the AI verification to return an approved result with score 1.0 (20 XP)
            # NOTE: We use a regular Mock instead of AsyncMock to avoid coroutine issues in threaded context
            # The actual verification logic is not what we're testing here - we're testing concurrency handling
            local_ai_service.verify_evidence = MagicMock(
                return_value=VerificationResult(
                    approved=True,
                    confidence=0.9,
                    score=1.0,
                    reason="Goal perfectly met",
                    missing=[]
                )
            )
            try:
                # Check session state before attempting verification
                session_pre = thread_session.query(FocusSession).filter(
                    FocusSession.id == session_id
                ).first()
                verification_status_before = session_pre.verification_status if session_pre else None
                if session_pre:
                    print(f"Thread {threading.get_ident()}: Session state before verification - status: {session_pre.status}, verification_status: {verification_status_before}")
                else:
                    print(f"Thread {threading.get_ident()}: Session not found before verification attempt")

                # This mimics the background task: get session with lock, process verification
                print(f"Thread {threading.get_ident()} querying for session {session_id}")
                session_obj = thread_session.query(FocusSession).filter(
                    FocusSession.id == session_id,
                    FocusSession.user_id == user_id
                ).with_for_update().first()
                print(f"Thread {threading.get_ident()} found session: {session_obj}")
                if not session_obj:
                    results.append(("error", "Session not found"))
                    return
                # Reload evidence (though empty)
                evidence_objs = local_focus_service.get_evidence_for_session(session_id)
                evidence_list = []
                for ev in evidence_objs:
                    evidence_list.append({
                        "type": ev.type,
                        "content": ev.content,
                        "file_path": ev.file_path
                    })
                # Verify the evidence (mocked)
                verification_result = local_ai_service.verify_evidence(
                    goal=session_obj.goal_text or "",
                    evidence=evidence_list,
                )
                # Store verification status before processing to determine if we awarded XP
                verification_status_before_processing = session_obj.verification_status
                # Process the result
                local_focus_service.process_ai_verification_result(
                    user_id, verification_result, session_obj
                )
                # Note: process_ai_verification_result commits the transaction
                # After processing, refresh to get final state
                thread_session.refresh(session_obj)
                print(f"Thread {threading.get_ident()} processed session {session_obj.id}: verification_status before={verification_status_before_processing}, after={session_obj.verification_status}, xp_awarded={session_obj.xp_awarded}")

                # Determine if this thread was successful:
                # Success: we changed verification_status from "pending" to "approved" (meaning we awarded XP)
                # Error: we found verification_status was not "pending" when we started (meaning another thread already processed it)
                if verification_status_before_processing == "pending" and session_obj.verification_status == "approved":
                    results.append(("success", session_obj.id))
                elif verification_status_before_processing != "pending":
                    results.append(("error", f"Verification status was not pending when we started: {verification_status_before_processing}"))
                else:
                    # verification_status_before_processing == "pending" but after processing it's not "approved"
                    results.append(("error", f"Verification processing did not result in approved status: {session_obj.verification_status}"))
            except Exception as e:
                import traceback
                print(f"Exception in AI verification thread {threading.get_ident()}: {e}")  # Debug
                traceback.print_exc()
                results.append(("error", str(e)))

    # Create two threads
    thread1 = threading.Thread(target=process_verification)
    thread2 = threading.Thread(target=process_verification)

    # Start both threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

    print(f"AI verification results: {results}")  # Debug

    # We expect one success and one error (because the second will see the verification status is no longer pending)
    success_count = sum(1 for r in results if r[0] == "success")
    error_count = sum(1 for r in results if r[0] == "error")
    assert success_count == 1, f"Expected 1 success, got {success_count}"
    assert error_count == 1, f"Expected 1 error, got {error_count}"

    # Check that only one XP transaction was created (20 XP for score 1.0)
    with db.session() as check_session:
        xp_transactions = check_session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        assert len(xp_transactions) == 1, f"Expected 1 XP transaction, got {len(xp_transactions)}"
        assert xp_transactions[0].amount == 20, f"Expected 20 XP, got {xp_transactions[0].amount}"


if __name__ == "__main__":
    # Run the tests directly
    pytest.main([__file__, "-v", "-s"])