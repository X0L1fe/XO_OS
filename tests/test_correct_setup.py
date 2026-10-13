#!/usr/bin/env python3
"""
Test with correct setup to ensure relevance check passes.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_with_correct_setup():
    """Test with user's selected_calendar_id matching target."""
    print("=== Testing with Correct Setup ===")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"  # This is what we want to switch TO

    print(f"Source calendar: {source_calendar_id}")
    print(f"Target calendar: {target_calendar_id}")
    print(f"For switch to proceed, user.selected_calendar_id should EQUAL target_calendar_id")

    # Create the actual lesson and event objects
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"
    test_lesson.subject = "Test Lesson"
    test_lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    test_lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    test_event_record = GoogleCalendarEvent()
    test_event_record.id = 201
    test_event_record.connection_id = 1
    test_event_record.google_event_id = test_lesson.google_event_id
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

    # Track session calls
    session_calls = []

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

            # SESSION 1: __init__ call for color overrides (happens when service is instantiated)
            # SESSION 2: Relevance check in switch_calendar_for_user
            # SESSION 3: Connection checks
            # SESSION 4: Get lessons
            # SESSION 5+: Process lessons

            if call_number == 1:
                # This could be either __init__ or relevance check
                if query_count == 1:
                    # First query in first session - could be User query for colors OR User query for relevance
                    print(f"    -> First query in first session")
                    # We need to distinguish based on context
                    # Let's assume first session is __init__, second is relevance check
                    user_mock = Mock()
                    user_mock.id = user_id
                    user_mock.lesson_colors = {}  # For __init__
                    user_mock.selected_calendar_id = target_calendar_id  # For relevance check

                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = user_mock
                    return query_mock
                else:
                    print(f"    -> Unexpected query in first session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            elif call_number == 2:
                # This should be the relevance check session
                if query_count == 1:
                    print(f"    -> Relevance check: getting user")
                    user_mock = Mock()
                    user_mock.id = user_id
                    user_mock.selected_calendar_id = target_calendar_id  # MATCH TARGET

                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = user_mock
                    return query_mock
                else:
                    print(f"    -> Unexpected query in relevance check session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            elif call_number == 3:
                # Connection check session
                if query_count == 1:
                    print(f"    -> Connection check: getting user")
                    user_mock = Mock()
                    user_mock.id = user_id
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = user_mock
                    return query_mock
                elif query_count == 2:
                    print(f"    -> Checking source connection")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = source_connection
                    return query_mock
                elif query_count == 3:
                    print(f"    -> Checking target connection")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = target_connection
                    return query_mock
                else:
                    print(f"    -> Unexpected query in connection check session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            elif call_number == 4:
                # Get lessons session
                if query_count == 1:
                    print(f"    -> Getting source connection")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = source_connection
                    return query_mock
                elif query_count == 2:
                    print(f"    -> Getting target connection")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = target_connection
                    return query_mock
                elif query_count == 3:
                    print(f"    -> Building lessons query")
                    query_mock = Mock()
                    join_mock = Mock()
                    filter1_mock = Mock()
                    filter2_mock = Mock()

                    query_mock.join.return_value = join_mock
                    join_mock.filter.return_value = filter1_mock
                    filter1_mock.filter.return_value = filter2_mock
                    filter2_mock.all.return_value = [test_lesson]
                    return query_mock
                else:
                    print(f"    -> Unexpected query in lessons session")
                    query_mock = Mock()
                    filter_mock = Mock()
                    query_mock.filter.return_value = filter_mock
                    filter_mock.first.return_value = None
                    return query_mock

            elif call_number >= 5:
                # Lesson processing sessions
                print(f"    -> Lesson processing session #{call_number}")
                if query_count == 1:
                    print(f"    -> Getting lesson to process")
                    query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()

                    query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_lesson
                    return query_mock
                elif query_count == 2:
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

            else:
                print(f"    -> Fallback for unknown session")
                query_mock = Mock()
                filter_mock = Mock()
                query_mock.filter.return_value = filter_mock
                query_mock.first.return_value = None
                return query_mock

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Mock service calls
    service_calls = []

    def get_service_mock(*args, **kwargs):
        call_number = len(service_calls) + 1
        service_calls.append(call_number)
        print(f"  SERVICE CALL #{call_number}")

        mock_service = Mock()
        mock_service.events = Mock(return_value=Mock())

        if call_number == 1:
            # Source service
            print(f"    -> Source service: get event")
            mock_service.events().get = Mock(return_value=Mock())
            mock_service.events().get().execute = Mock(return_value=source_event)
            print(f"    -> Source service: delete event")
            mock_service.events().delete = Mock(return_value=Mock())
            mock_service.events().delete().execute = Mock(return_value=None)
        else:
            # Target service
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
                else:
                    print("❌ FAILURE: Expected 1 processed lesson")

            except Exception as e:
                print(f"\n=== EXCEPTION ===")
                print(f"Exception: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    test_with_correct_setup()