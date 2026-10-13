#!/usr/bin/env python3
"""
Test the actual flow of switch_calendar_for_user to see where it's failing.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_actual_flow():
    """Test the actual flow with proper mocking."""
    print("Testing actual flow...")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    print(f"source: {source_calendar_id}")
    print(f"target: {target_calendar_id}")

    # Create mock objects
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"

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

    # Track ALL session calls
    session_calls = []

    def session_mock(*args, **kwargs):
        call_number = len(session_calls) + 1
        session_calls.append(call_number)
        print(f"\n=== SESSION CALL #{call_number} ===")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_count = 0

        def query_side_effect(*query_args):
            nonlocal query_count
            query_count += 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])
            print(f"  Query #{query_count}: {query_type}")

            # Handle the queries in the order they appear in the actual code

            # FIRST session: relevance check (lines 1118-1130)
            if call_number == 1:
                if query_count == 1:
                    # Query: session.query(User).filter(User.id == user_id).first()
                    print(f"    -> Relevance check: getting user {user_id}")
                    user_mock = Mock()
                    user_mock.id = user_id
                    user_mock.selected_calendar_id = target_calendar_id  # MATCH TARGET for relevance
                    print(f"    -> User selected_calendar_id: '{user_mock.selected_calendar_id}'")
                    print(f"    -> Target calendar_id: '{target_calendar_id}'")
                    print(f"    -> Relevance check (selected != target): {user_mock.selected_calendar_id != target_calendar_id}")
                    mock_query = Mock()
                    mock_query.first.return_value = user_mock
                    return mock_query
                else:
                    print(f"    -> Unexpected query in relevance check session")
                    mock_query = Mock()
                    mock_query.first.return_value = None
                    return mock_query

            # SECOND session: connection check (lines 1132-1154)
            elif call_number == 2:
                if query_count == 1:
                    # Query: session.query(User).filter(User.id == user_id).first()
                    # (done again at line 1133? No wait, let me check the code...)
                    # Actually line 1133 starts a NEW session: "with db.session() as session:"
                    # So this is a SECOND session for connection checking
                    print(f"    -> Connection check: getting user {user_id}")
                    user_mock = Mock()
                    user_mock.id = user_id
                    # This user object isn't actually used for relevance in this session,
                    # but we need to return something
                    mock_query = Mock()
                    mock_query.first.return_value = user_mock
                    return mock_query
                elif query_count == 2:
                    # Query: session.query(GoogleCalendarConnection).filter(...source...).first()
                    print(f"    -> Checking source connection for {source_calendar_id}")
                    mock_query = Mock()
                    mock_query.first.return_value = source_connection
                    print(f"    -> Source connection result: {source_connection is not None}")
                    return mock_query
                elif query_count == 3:
                    # Query: session.query(GoogleCalendarConnection).filter(...target...).first()
                    print(f"    -> Checking target connection for {target_calendar_id}")
                    mock_query = Mock()
                    mock_query.first.return_value = target_connection
                    print(f"    -> Target connection result: {target_connection is not None}")
                    return mock_query
                else:
                    print(f"    -> Unexpected query in connection check session")
                    mock_query = Mock()
                    mock_query.first.return_value = None
                    return mock_query

            # THIRD session: get connections and lessons (lines 1161-1198)
            elif call_number == 3:
                if query_count == 1:
                    # Query: session.query(GoogleCalendarConnection).filter(...source...).first()
                    print(f"    -> Getting source connection (again) for {source_calendar_id}")
                    mock_query = Mock()
                    mock_query.first.return_value = source_connection
                    return mock_query
                elif query_count == 2:
                    # Query: session.query(GoogleCalendarConnection).filter(...target...).first()
                    print(f"    -> Getting target connection (again) for {target_calendar_id}")
                    mock_query = Mock()
                    mock_query.first.return_value = target_connection
                    return mock_query
                elif query_count >= 3:
                    # Query: the complex lessons join query
                    print(f"    -> Building lessons query (join + filter + filter + all)")
                    mock_query = Mock()
                    mock_query.join.return_value = mock_query  # join
                    mock_query.filter.return_value = mock_query  # filter (user_id)
                    mock_query.filter.return_value = mock_query  # filter (connection_id)
                    mock_query.all.return_value = [test_lesson]  # all()
                    print(f"    -> Lessons query returning {len([test_lesson])} lessons")
                    return mock_query
                else:
                    print(f"    -> Unexpected query in lessons session")
                    mock_query = Mock()
                    mock_query.first.return_value = None
                    return mock_query

            # FOURTH+ sessions: processing individual lessons (lines 1209+)
            else:
                print(f"    -> Inner lesson processing session #{call_number}")
                if query_count == 1:
                    # Query: lesson_session.query(Lesson).filter(Lesson.id == lesson.id).with_for_update().first()
                    print(f"    -> Getting lesson to process (ID: {test_lesson.id})")
                    mock_query = Mock()
                    mock_query.filter.return_value = mock_query
                    mock_query.with_for_update.return_value = mock_query
                    mock_query.first.return_value = test_lesson
                    return mock_query
                elif query_count == 2:
                    # Query: lesson_session.query(GoogleCalendarEvent).filter(...).with_for_update().first()
                    print(f"    -> Getting event record to process")
                    mock_query = Mock()
                    mock_query.filter.return_value = mock_query
                    mock_query.with_for_update.return_value = mock_query
                    mock_query.first.return_value = Mock()  # Return a mock event record
                    return mock_query
                else:
                    print(f"    -> Unexpected query in lesson processing session")
                    mock_query = Mock()
                    mock_query.first.return_value = None
                    return mock_query

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
            # Source service: get event
            mock_service.events().get = Mock(return_value=Mock())
            mock_service.events().get().execute = Mock(return_value={
                "id": "event_123",
                "summary": "Test Lesson",
                "start": {"dateTime": "2026-10-08T19:00:00Z"},
                "end": {"dateTime": "2026-10-08T20:00:00Z"},
            })
            # Source service: delete event
            mock_service.events().delete = Mock(return_value=Mock())
            mock_service.events().delete().execute = Mock(return_value=None)
        else:
            # Target service: create event
            mock_service.events().insert = Mock(return_value=Mock())
            mock_service.events().insert().execute = Mock(return_value={"id": "new_event_456"})

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
    test_actual_flow()