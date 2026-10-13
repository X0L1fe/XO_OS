#!/usr/bin/env python3
"""
Working test for switch_calendar_for_user - based on final_test.py that worked.
Fixed to properly set up user mock for relevance check.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_switch_calendar_for_user_success():
    """Test successful calendar switching - based on working final_test.py."""
    print("Test: Successful calendar switching")

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

    # Track session calls
    session_calls = []
    service_calls = []

    def session_mock(*args, **kwargs):
        session_calls.append(len(session_calls) + 1)
        call_num = len(session_calls)
        print(f"Session call #{call_num}")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        # Track query number within this session
        query_num = 0

        def query_side_effect(*args):
            nonlocal query_num
            query_num += 1
            query_type = args[0].__name__ if hasattr(args[0], '__name__') else str(args[0])
            print(f"    Query #{query_num} ({query_type}) with args: {args}")

            if call_num == 1:
                # This is the session from GoogleCalendarSyncService.__init__ (for user colors)
                if query_num == 1:
                    # Query for User to get color overrides
                    print("      Returning User for color overrides")
                    # FIXED: Set selected_calendar_id to match target for relevance check to PASS
                    user_mock = Mock()
                    user_mock.id = user_id
                    user_mock.selected_calendar_id = target_calendar_id  # IMPORTANT: Match target
                    user_mock.lesson_colors = {}  # Empty colors for __init__
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    user_filter_mock.first.return_value = user_mock
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                else:
                    return Mock()
            elif call_num == 2:
                # This is the outer session in switch_calendar_for_user (for connections and lessons)
                if query_num == 1:
                    # First query: source_connection
                    print("      Returning source_connection")
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    connection_filter_mock.first.return_value = source_connection
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif query_num == 2:
                    # Second query: target_connection
                    print("      Returning target_connection")
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    connection_filter_mock.first.return_value = target_connection
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif query_num >= 3:
                    # Third query+: lessons (the complex join query)
                    print("      Building lessons query mock chain")
                    # Build the mock chain properly: each method returns self for chaining, except .all()

                    # Start with the query mock for Lesson
                    lesson_query_mock = Mock()
                    print("      Created lesson_query_mock")

                    # Mock .join(GoogleCalendarEvent, Lesson.google_event_id == GoogleCalendarEvent.google_event_id)
                    # For chaining, .join() should return the query object itself
                    lesson_query_mock.join.return_value = lesson_query_mock
                    print("      Set up join to return self")

                    # Mock first .filter(Lesson.user_id == user_id)
                    # For chaining, .filter() should return the query object itself
                    lesson_query_mock.filter.return_value = lesson_query_mock
                    print("      Set up first filter to return self")

                    # Mock second .filter(GoogleCalendarEvent.connection_id == source_connection.id)
                    # For chaining, .filter() should return the query object itself
                    lesson_query_mock.filter.return_value = lesson_query_mock
                    print("      Set up second filter to return self")

                    # Mock .all() to return our lessons list (this should return the actual list containing our lesson instance)
                    result_list = [test_lesson]  # Return a REAL list containing our test_lesson instance
                    lesson_query_mock.all.return_value = result_list
                    print(f"      Set up all() to return list with {len(result_list)} lesson(s)")
                    print(f"      First lesson in list ID: {result_list[0].id if result_list else 'None'}")

                    return lesson_query_mock
                else:
                    return Mock()
            else:
                # These are inner sessions (for processing each lesson)
                print(f"      Setting up inner session #{call_num}")
                if query_num == 1:
                    # First query: get lesson to process (with for_update)
                    print("        Returning lesson to process query")
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = test_lesson  # RETURN THE SAME LESSON INSTANCE
                    return lesson_query_mock
                elif query_num == 2:
                    # Second query: get event record (with for_update)
                    print("        Returning event record query")
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = test_event_record  # RETURN THE SAME EVENT INSTANCE
                    return event_query_mock
                else:
                    return Mock()

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Mock the get_google_calendar_service function
    service_calls = []

    def get_service_mock(*args, **kwargs):
        service_calls.append(len(service_calls) + 1)
        call_num = len(service_calls)
        print(f"get_google_calendar_service call #{call_num}")

        mock_service = Mock()
        if call_num == 1:
            # Source service
            print("      Returning source service")
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(return_value=source_event)

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)
        else:
            # Target service
            print("      Returning target service")
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(return_value=created_event)
        return mock_service

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # Call the method
            print("Calling switch_calendar_for_user...")
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )

            print(f"\nResult: {result}")
            print(f"Session calls: {len(session_calls)}")
            print(f"Service calls: {len(service_calls)}")

            # Assertions - DO NOT PRINT HERE TO AVOID UNICODE ISSUES
            assert result == 1, f"Expected 1 processed lesson, got {result}"
            # Check that the lesson's google_event_id was updated (same object reference)
            assert test_lesson.google_event_id == "new_event_456"
            # Check that the event record was updated
            assert test_event_record.connection_id == target_connection.id
            assert test_event_record.google_event_id == "new_event_456"
            assert test_event_record.calendar_id == target_calendar_id


if __name__ == "__main__":
    # Run the tests exactly like final_test.py did
    test_switch_calendar_for_user_success()
    print("\nTest passed! ✅")