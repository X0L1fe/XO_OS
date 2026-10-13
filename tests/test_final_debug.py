#!/usr/bin/env python3
"""
Final debug test - combining everything with proper mocking.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_complete_flow():
    """Test the complete flow with proper mocking."""
    print("=== Testing Complete Flow ===")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Create the actual lesson and event objects we'll share throughout
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"
    test_lesson.subject = "Test Lesson"
    test_lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    test_lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    test_event_record = GoogleCalendarEvent()
    test_event_record.id = 201
    test_event_record.connection_id = 1  # Will be set properly later
    test_event_record.google_event_id = test_lesson.google_event_id  # Share same ID initially
    test_event_record.calendar_id = source_calendar_id
    test_event_record.summary = test_lesson.subject
    test_event_record.start_time = test_lesson.start_time
    test_event_record.end_time = test_lesson.end_time

    # Mock connections
    source_connection = Mock()
    source_connection.id = 1
    source_connection.user_id = user_id
    source_connection.calendar_id = source_calendar_id
    source_connection.enabled = 1

    target_connection = Mock()
    target_connection.id = 2
    target_connection.user_id = user_id
    target_connection.calendar_id = target_calendar_id
    target_connection.enabled = 1

    # Mock Google Calendar API responses
    source_event = {
        "id": "event_123",
        "summary": "Test Lesson",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed",
    }

    created_event = {
        "id": "new_event_456",
        "summary": "Test Lesson",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed",
    }

    # Track ALL session calls
    session_calls = []
    service_calls = []

    def session_mock(*args, **kwargs):
        call_number = len(session_calls) + 1
        session_calls.append(call_number)
        print(f"\n--- SESSION CALL #{call_number} ---")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_count = 0

        def query_side_effect(*query_args):
            nonlocal query_count
            query_count += 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])
            print(f"  Query #{query_count}: {query_type}")

            # SESSION 1: Relevance check (lines 1118-1130)
            if call_number == 1:
                if query_count == 1:
                    # Query: session.query(User).filter(User.id == user_id).first()
                    print(f"    -> Relevance check: getting user {user_id}")
                    # Create user mock with proper attribute chaining
                    user_mock = Mock()
                    user_mock.id = user_id
                    user_mock.selected_calendar_id = target_calendar_id  # MATCH TARGET for relevance check

                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = user_mock

                    print(f"    -> User selected_calendar_id: '{user_mock.selected_calendar_id}'")
                    print(f"    -> Target calendar_id: '{target_calendar_id}'")
                    relevance_check = user_mock.selected_calendar_id != target_calendar_id
                    print(f"    -> Relevance check (selected != target): {relevance_check}")
                    return query_mock
                else:
                    print(f"    -> Unexpected query in relevance check session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            # SESSION 2: Connection check (lines 1132-1154)
            elif call_number == 2:
                if query_count == 1:
                    # Query: session.query(User).filter(User.id == user_id).first()
                    # (This happens again at line 1133 in the connection check session)
                    print(f"    -> Connection check: getting user {user_id}")
                    user_mock = Mock()
                    user_mock.id = user_id
                    # We don't actually use this user object for logic in this session
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = user_mock
                    return query_mock
                elif query_count == 2:
                    # Query: session.query(GoogleCalendarConnection).filter(...source...).first()
                    print(f"    -> Checking source connection for {source_calendar_id}")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = source_connection
                    print(f"    -> Source connection result: {source_connection is not None}")
                    return query_mock
                elif query_count == 3:
                    # Query: session.query(GoogleCalendarConnection).filter(...target...).first()
                    print(f"    -> Checking target connection for {target_calendar_id}")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = target_connection
                    print(f"    -> Target connection result: {target_connection is not None}")
                    return query_mock
                else:
                    print(f"    -> Unexpected query in connection check session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            # SESSION 3: Get connections and lessons (lines 1161-1198)
            elif call_number == 3:
                if query_count == 1:
                    # Query: session.query(GoogleCalendarConnection).filter(...source...).first()
                    print(f"    -> Getting source connection (again) for {source_calendar_id}")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = source_connection
                    return query_mock
                elif query_count == 2:
                    # Query: session.query(GoogleCalendarConnection).filter(...target...).first()
                    print(f"    -> Getting target connection (again) for {target_calendar_id}")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = target_connection
                    return query_mock
                elif query_count >= 3:
                    # Query: the complex lessons join query
                    print(f"    -> Building lessons query (join + filter + filter + all)")
                    query_mock = Mock()
                    join_mock = Mock()
                    filter1_mock = Mock()
                    filter2_mock = Mock()

                    # Set up proper chaining: query -> join -> filter -> filter -> all
                    query_mock.join.return_value = join_mock
                    join_mock.filter.return_value = filter1_mock
                    filter1_mock.filter.return_value = filter2_mock
                    filter2_mock.all.return_value = [test_lesson]  # Return our lesson

                    print(f"    -> Lessons query returning {len([test_lesson])} lessons")
                    return query_mock
                else:
                    print(f"    -> Unexpected query in lessons session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            # SESSION 4+: Processing individual lessons (lines 1209+)
            else:
                print(f"    -> Inner lesson processing session #{call_number}")
                if query_count == 1:
                    # Query: lesson_session.query(Lesson).filter(Lesson.id == lesson.id).with_for_update().first()
                    print(f"    -> Getting lesson to process (ID: {test_lesson.id})")
                    query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()

                    query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_lesson
                    return query_mock
                elif query_count == 2:
                    # Query: lesson_session.query(GoogleCalendarEvent).filter(...).with_for_update().first()
                    print(f"    -> Getting event record to process")
                    query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()

                    query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_event_record
                    return query_mock
                else:
                    print(f"    -> Unexpected query in lesson processing session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Mock service calls
    def get_service_mock(*args, **kwargs):
        call_number = len(service_calls) + 1
        service_calls.append(call_number)
        print(f"  SERVICE CALL #{call_number}")

        mock_service = Mock()
        mock_service.events = Mock(return_value=Mock())

        if call_number == 1:
            # Source service: get event and delete event
            print(f"    -> Source service: get event")
            mock_service.events().get = Mock(return_value=Mock())
            mock_service.events().get().execute = Mock(return_value=source_event)

            print(f"    -> Source service: delete event")
            mock_service.events().delete = Mock(return_value=Mock())
            mock_service.events().delete().execute = Mock(return_value=None)
        else:
            # Target service: create event
            print(f"    -> Target service: create event")
            mock_service.events().insert = Mock(return_value=Mock())
            mock_service.events().insert().execute = Mock(return_value=created_event)

        return mock_service

    # Run the test
    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            print("Calling switch_calendar_for_user...")
            try:
                result = GoogleCalendarSyncService.switch_calendar_for_user(
                    db, user_id, source_calendar_id, target_calendar_id
                )
                print(f"\n=== FINAL RESULT ===")
                print(f"Result: {result}")
                print(f"Total session calls: {len(session_calls)}")
                print(f"Total service calls: {len(service_calls)}")

                if result == 1:
                    print("✅ SUCCESS: Test passed!")
                    # Verify the objects were updated correctly
                    print(f"Lesson google_event_id: {test_lesson.google_event_id}")
                    print(f"Event record connection_id: {test_event_record.connection_id}")
                    print(f"Event record google_event_id: {test_event_record.google_event_id}")
                    print(f"Event record calendar_id: {test_event_record.calendar_id}")
                else:
                    print("❌ FAILURE: Expected 1 processed lesson")

            except Exception as e:
                print(f"\n=== EXCEPTION ===")
                print(f"Exception: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    test_complete_flow()