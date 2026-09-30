"""
Simple test to verify that .with_for_update() works as expected in SQLite
"""
import threading
import time
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from app.database.db import Database
from app.database.models import User, FocusSession


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


def test_simple_locking():
    """Test basic locking behavior"""
    # Create a file-based SQLite database for testing
    import tempfile
    import os
    tmp_dir = tempfile.mkdtemp()
    db_path = os.path.join(tmp_dir, "test.db")
    db = Database(f"sqlite:///{db_path}")

    # Create test data
    with db.session() as session:
        user = create_test_user(session)
        focus_session = FocusSession(
            user_id=user.id,
            goal_text="Test goal",
            status="active",
            started_at=datetime.now(timezone.utc),
        )
        session.add(focus_session)
        session.commit()
        session.refresh(focus_session)
        session_id = focus_session.id
        print(f"Created focus session {session_id}")

    results = []

    def access_session(thread_num):
        """Each thread tries to read and update the session"""
        with db.session() as thread_session:
            # Try to lock and read the session
            session_obj = thread_session.query(FocusSession).filter(
                FocusSession.id == session_id
            ).with_for_update().first()

            if session_obj:
                print(f"Thread {thread_num}: Got session, status={session_obj.status}")
                # Simulate some work
                time.sleep(0.1)
                # Try to update it
                session_obj.status = "processed"
                thread_session.commit()
                results.append((thread_num, "success", session_obj.id))
                print(f"Thread {thread_num}: Updated session to processed")
            else:
                results.append((thread_num, "none", None))
                print(f"Thread {thread_num}: No session found")

    # Create two threads
    thread1 = threading.Thread(target=access_session, args=(1,))
    thread2 = threading.Thread(target=access_session, args=(2,))

    # Start threads
    thread1.start()
    time.sleep(0.01)  # Small stagger
    thread2.start()

    # Wait for completion
    thread1.join()
    thread2.join()

    print(f"Results: {results}")

    # Check final state
    with db.session() as check_session:
        final_session = check_session.query(FocusSession).filter(
            FocusSession.id == session_id
        ).first()
        print(f"Final session status: {final_session.status if final_session else 'None'}")

    # Cleanup
    import shutil
    shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    test_simple_locking()