import sys
sys.path.insert(0, 'D:\\Projects\\XO_OS')
from app.database.db import Database
from app.database.models import Lesson, User, ScheduleExclusion
from app.focus.service import FocusService
from datetime import datetime, timedelta, timezone
import uuid

def test_get_current_lesson():
    db = Database()
    with db.session() as session:
        # Clean up any previous test data for this run
        session.query(ScheduleExclusion).filter(ScheduleExclusion.value_key.in_(['ELECTIVE'])).delete()
        session.query(Lesson).filter(Lesson.subject.like('Test%')).delete()
        session.query(User).filter(User.email.like('test%@example.com')).delete()
        session.commit()

        # Create a test user
        user = User(
            email='testfix@example.com',
            name='Test Fix User',
            password_hash='dummy',  # We won't actually use the password for this test
            email_verified=1,
            is_active=1,
            onboarding_completed=0
        )
        session.add(user)
        session.commit()
        user_id = user.id
        print(f"Created test user with ID: {user_id}")

        now = datetime.now(timezone.utc)
        # Create a visible lesson (REGULAR) happening now
        visible_lesson = Lesson(
            user_id=user_id,
            subject="Test Visible",
            category="REGULAR",
            lesson_type="LECTURE",
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(minutes=50),
            description="Test visible lesson",
            room="101",
            teacher="Mr. Test",
            content_hash="dummy",
            google_event_id=None,
            stable_id=str(uuid.uuid4())
        )
        # Create an excluded lesson (ELECTIVE) happening now
        excluded_lesson = Lesson(
            user_id=user_id,
            subject="Test Excluded",
            category="ELECTIVE",
            lesson_type="LECTURE",
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(minutes=50),
            description="Test excluded lesson",
            room="102",
            teacher="Ms. Test",
            content_hash="dummy",
            google_event_id=None,
            stable_id=str(uuid.uuid4())
        )
        session.add_all([visible_lesson, excluded_lesson])
        session.commit()
        print(f"Created visible lesson ID: {visible_lesson.id}")
        print(f"Created excluded lesson ID: {excluded_lesson.id}")

        # Set schedule exclusions: exclude ELECTIVE category
        excl = ScheduleExclusion(
            user_id=user_id,
            exclusion_type="category",
            value_key="ELECTIVE",
            value_label="Элективы"
        )
        session.add(excl)
        session.commit()
        print("Added schedule exclusion for ELECTIVE category")

        # Now test get_current_lesson
        focus_service = FocusService(session)
        lesson = focus_service.get_current_lesson(user_id)

        if lesson is None:
            print("ERROR: get_current_lesson returned None")
            return False
        else:
            print(f"get_current_lesson returned lesson ID: {lesson.id}, subject: {lesson.subject}, category: {lesson.category}")
            # Check that it's the visible lesson
            if lesson.id == visible_lesson.id:
                print("SUCCESS: get_current_lesson returned the visible lesson")
                success = True
            else:
                print(f"ERROR: get_current_lesson returned lesson {lesson.id} but expected visible lesson {visible_lesson.id}")
                success = False

        # Clean up
        session.delete(visible_lesson)
        session.delete(excluded_lesson)
        session.delete(excl)
        session.delete(user)
        session.commit()
        print("Cleaned up test data")

        return success

if __name__ == "__main__":
    if test_get_current_lesson():
        print("Test PASSED")
        sys.exit(0)
    else:
        print("Test FAILED")
        sys.exit(1)