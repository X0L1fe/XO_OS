import sys
sys.path.insert(0, 'D:\\Projects\\XO_OS')
from app.database.db import Database
from app.database.models import Lesson, User, ScheduleExclusion
from datetime import datetime, timedelta, timezone
import uuid
import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8000"

def http_post(url, data=None, cookies=None):
    data_encoded = json.dumps(data).encode('utf-8') if data else None
    req = urllib.request.Request(url, data=data_encoded, headers={'Content-Type': 'application/json'})
    if cookies:
        for cookie in cookies:
            req.add_header('Cookie', f'{cookie.name}={cookie.value}')
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = response.read().decode('utf-8')
            resp_cookies = response.headers.get_all('Set-Cookie') or []
            return response.status, resp_data, resp_cookies
    except urllib.error.HTTPError as e:
        resp_data = e.read().decode('utf-8') if e.read() else ''
        resp_cookies = e.headers.get_all('Set-Cookie') or []
        return e.code, resp_data, resp_cookies

def http_get(url, cookies=None):
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    if cookies:
        for cookie in cookies:
            req.add_header('Cookie', f'{cookie.name}={cookie.value}')
    try:
        with urllib.request.urlopen(req) as response:
            resp_data = response.read().decode('utf-8')
            resp_cookies = response.headers.get_all('Set-Cookie') or []
            return response.status, resp_data, resp_cookies
    except urllib.error.HTTPError as e:
        resp_data = e.read().decode('utf-8') if e.read() else ''
        resp_cookies = e.headers.get_all('Set-Cookie') or []
        return e.code, resp_data, resp_cookies

def main():
    # Step 1: Create test user and lesson via DB
    db = Database()
    with db.session() as session:
        # Clean up any previous test data for this run
        session.query(ScheduleExclusion).filter(ScheduleExclusion.value_key.in_(['ELECTIVE'])).delete()
        session.query(Lesson).filter(Lesson.subject.like('Test%')).delete()
        session.query(User).filter(User.email.like('testapi%@example.com')).delete()
        session.commit()

        # Create a test user
        user = User(
            email='testapi@example.com',
            name='Test API User',
            password_hash='dummy',  # We'll set a real password via the auth service later, but for now we need to hash a password.
            email_verified=1,
            is_active=1,
            onboarding_completed=0
        )
        # We need to set a real password hash so we can login.
        from app.auth.service import get_password_hash
        user.password_hash = get_password_hash('testpass')
        session.add(user)
        session.commit()
        user_id = user.id
        print(f"Created test user with ID: {user_id}")

        now = datetime.now(timezone.utc)
        # Create a visible lesson (REGULAR) happening now
        visible_lesson = Lesson(
            user_id=user_id,
            subject="Test Visible API",
            category="REGULAR",
            lesson_type="LECTURE",
            start_time=now - timedelta(minutes=10),
            end_time=now + timedelta(minutes=50),
            description="Test visible lesson for API",
            room="101",
            teacher="Mr. Test",
            content_hash="dummy",
            google_event_id=None,
            stable_id=str(uuid.uuid4())
        )
        session.add(visible_lesson)
        session.commit()
        lesson_id = visible_lesson.id
        print(f"Created visible lesson ID: {lesson_id}")

        # We don't set any exclusions for this test so that the lesson is visible.

    # Step 2: Login via API
    print("Logging in via API...")
    status, data, new_cookies = http_post(f"{BASE_URL}/api/auth/login",
                                          data={"email": "testapi@example.com", "password": "testpass"})
    if status != 200:
        print(f"Login failed: {status} {data}")
        return False
    # Extract session token
    session_cookie = None
    for cookie in new_cookies:
        if cookie.name == 'session_token':
            session_cookie = cookie.value
            break
    if not session_cookie:
        print("No session cookie found")
        return False
    print("Login successful")
    cookies = [http.cookiejar.Cookie(version=0, name='session_token', value=session_cookie,
                                     port=None, port_specified=False, domain='127.0.0.1', domain_specified=False,
                                     domain_initial_dot=False, path='/', path_specified=True,
                         secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={})]

    # Step 3: Start a focus session
    print("Starting focus session via API...")
    status, data, new_cookies = http_post(f"{BASE_URL}/api/focus/start",
                                          cookies=cookies)
    if status != 200:
        print(f"Focus start failed: {status} {data}")
        return False
    for cookie in new_cookies:
        cookies.append(cookie)
    focus_data = json.loads(data)
    print(f"Focus start response: {json.dumps(focus_data, indent=2)}")
    returned_lesson_id = focus_data.get("lesson_id")
    if returned_lesson_id is None:
        print("ERROR: lesson_id is null in focus start response")
        return False
    if returned_lesson_id != lesson_id:
        print(f"ERROR: returned lesson_id {returned_lesson_id} does not match created lesson_id {lesson_id}")
        return False
    print(f"SUCCESS: lesson_id matches: {returned_lesson_id}")

    # Step 4: Check /api/now
    print("Checking /api/now via API...")
    status, data, new_cookies = http_get(f"{BASE_URL}/api/now",
                                         cookies=cookies)
    if status != 200:
        print(f"/api/now failed: {status} {data}")
        return False
    for cookie in new_cookies:
        cookies.append(cookie)
    now_data = json.loads(data)
    if now_data.get("type") != "lesson":
        print(f"ERROR: /api/now type is {now_data.get('type')}, expected 'lesson'")
        return False
    if now_data.get("lesson_id") != lesson_id:
        print(f"ERROR: /api/now lesson_id {now_data.get('lesson_id')} does not match {lesson_id}")
        return False
    print(f"SUCCESS: /api/now lesson_id matches: {now_data.get('lesson_id')}")

    # Step 5: Clean up via DB
    print("Cleaning up via DB...")
    db = Database()
    with db.session() as session:
        # Delete the lesson
        lesson_to_delete = session.query(Lesson).filter(Lesson.id == lesson_id).first()
        if lesson_to_delete:
            session.delete(lesson_to_delete)
            print(f"Deleted lesson {lesson_id}")
        # Delete the user
        user_to_delete = session.query(User).filter(User.email == 'testapi@example.com').first()
        if user_to_delete:
            session.delete(user_to_delete)
            print(f"Deleted user testapi@example.com")
        session.commit()
    print("API integration test completed successfully.")
    return True

if __name__ == "__main__":
    if main():
        print("Test PASSED")
        sys.exit(0)
    else:
        print("Test FAILED")
        sys.exit(1)