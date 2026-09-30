"""
Debug script to understand the race condition test failure
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


def debug_manual_completion_race_condition():
    """Debug version of the manual completion race condition test"""
    # Create a file-based SQLite database for testing
    import tempfile
    import os
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test.db")
    db = Database(f"sqlite:///{db_path}")

    with db.session() as session:
        # Create test data
        user = create_test_user(session)
        lesson = create_test_lesson(session, user.id)
        user_id = user.id
        lesson_id = lesson.id

        # Create a focus session
        focus_session = create_test_focus_session(session, user_id, lesson_id)
        session_id = focus_session.id
        print(f"Created focus session with id: {session_id}")

    # We'll store the results from each thread
    results = []
    session_details = []  # To store what each thread sees

    def complete_session(thread_num):
        # Each thread creates its own session and focus service
        with db.session() as thread_session:
            thread_focus_service = FocusService(thread_session)
            try:
                # Let's see what the session looks like before attempting completion
                session_before = thread_session.query(FocusSession).filter(
                    FocusSession.id == session_id
                ).with_for_update().first()
                print(f"Thread {thread_num}: Session before completion - status: {session_before.status}, verification_status: {session_before.verification_status}")

                completed_session = thread_focus_service.complete_focus_session(
                    session_id=session_id,
                    user_id=user_id,
                    completion_mode="manual"
                )
                results.append(("success", completed_session.id))
                print(f"Thread {thread_num}: Success - completed session {completed_session.id}, xp_awarded: {completed_session.xp_awarded}")
            except Exception as e:
                import traceback
                print(f"Thread {thread_num}: Exception: {e}")
                traceback.print_exc()
                results.append(("error", str(e)))

    # Create two threads
    thread1 = threading.Thread(target=complete_session, args=(1,))
    thread2 = threading.Thread(target=complete_session, args=(2,))

    # Start both threads with a small stagger
    thread1.start()
    # Small delay to increase chance of proper ordering
    import time
    time.sleep(0.01)
    thread2.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

    print(f"Final Results: {results}")

    # Check final state
    with db.session() as check_session:
        final_session = check_session.query(FocusSession).filter(
            FocusSession.id == session_id
        ).first()
        print(f"Final session state - status: {final_session.status}, verification_status: {final_session.verification_status}, xp_awarded: {final_session.xp_awarded}")

        xp_transactions = check_session.query(XPTransaction).filter(
            XPTransaction.user_id == user_id
        ).all()
        print(f"Total XP transactions: {len(xp_transactions)}")
        for i, tx in enumerate(xp_transactions):
            print(f"  TX {i}: amount={tx.amount}, reason={tx.reason}")

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    debug_manual_completion_race_condition()