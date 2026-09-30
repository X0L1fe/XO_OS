"""
Debug version of the actual test to see what's different
"""
import threading
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.database.db import Database
from app.database.models import User, UserStats, FocusSession, FocusEvidence, Lesson, ScheduleExclusion, XPTransaction
from app.focus.service import FocusService
from app.ai.verification import AIVerificationService, VerificationResult


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


def test_manual_completion_race_condition():
    """Debug version of the actual test"""
    # Create a file-based SQLite database for testing - SAME AS TEST
    import tempfile
    import os
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test.db")
    db = Database(f"sqlite:///{db_path}")

    # Mimic the test fixtures exactly
    with db.session() as session:
        test_user = create_test_user(session)
        test_lesson = create_test_lesson(session, test_user.id)
        user_id = test_user.id
        lesson_id = test_lesson.id

        # Create a focus session in the database using a temporary session (so that it's committed and visible to other sessions)
        with db.session() as temp_session:
            focus_session = create_test_focus_session(temp_session, user_id, lesson_id)
            session_id = focus_session.id
            # Commit is done inside create_test_focus_session
            print(f"Created focus session with id: {session_id} in temp session")

    # We'll store the results from each thread
    results = []

    def complete_session():
        # Each thread creates its own session and focus service
        with db.session() as thread_session:
            thread_focus_service = FocusService(thread_session)
            try:
                # DEBUG: Let's see what the session looks like
                session_check = thread_session.query(FocusSession).filter(
                    FocusSession.id == session_id
                ).first()
                print(f"Thread checking session: status={session_check.status}, verification_status={session_check.verification_status}")

                completed_session = thread_focus_service.complete_focus_session(
                    session_id=session_id,
                    user_id=user_id,
                    completion_mode="manual"
                )
                results.append(("success", completed_session.id))
                print(f"Thread success: completed session {completed_session.id}, xp_awarded: {completed_session.xp_awarded}")
            except Exception as e:
                import traceback
                print(f"Thread Exception: {e}")
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

    print(f"Results: {results}")

    # We expect one success and one error (because the second will see the session is no longer active/paused)
    success_count = sum(1 for r in results if r[0] == "success")
    error_count = sum(1 for r in results if r[0] == "error")
    print(f"Success count: {success_count}, Error count: {error_count}")

    # Check that only one XP transaction was created
    with db.session() as check_session:
        xp_transactions = check_session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        print(f"XP transactions count: {len(xp_transactions)}")
        for i, tx in enumerate(xp_transactions):
            print(f"  TX {i}: amount={tx.amount}, reason={tx.reason}")
        assert len(xp_transactions) == 1, f"Expected 1 XP transaction, got {len(xp_transactions)}"
        assert xp_transactions[0].amount == 3, f"Expected 3 XP, got {xp_transactions[0].amount}"

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    test_manual_completion_race_condition()