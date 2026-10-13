#!/usr/bin/env python3
"""Debug test for switch_calendar_for_user - attempt 4."""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_debug():
    """Debug the switch_calendar_for_user method."""
    print("Debug: Testing switch_calendar_for_user")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

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

    # Mock lesson and event
    lesson = Mock()
    lesson.id = 101
    lesson.user_id = user_id
    lesson.google_event_id = "event_123"
    lesson.subject = "Test Lesson"
    lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    event_record = Mock()
    event_record.id = 201
    event_record.connection_id = source_connection.id
    event_record.google_event_id = lesson.google_event_id
    event_record.calendar_id = source_calendar_id
    event_record.summary = lesson.subject
    event_record.start_time = lesson.start_time
    event_record.end_time = lesson.end_time

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

    # Track session calls and query types
    session_calls = []
    query_log = []  # List of (call_num, query_type, query_args)

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
            query_log.append((call_num, query_num, query_type, args))
            print(f"    Query #{query_num} ({query_type}) with args: {args}")

            if call_num == 1:
                # Outer session - handle connection and lessons queries
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
                    print("      Returning lessons query result")
                    # Build the mock chain: session.query(Lesson) -> .join() -> .filter() -> .filter() -> .all()

                    # Start with the query mock for Lesson
                    lesson_query_mock = Mock()

                    # Mock .join(GoogleCalendarEvent, Lesson.google_event_id == GoogleCalendarEvent.google_event_id)
                    join_mock = Mock()
                    lesson_query_mock.join.return_value = join_mock

                    # Mock first .filter(Lesson.user_id == user_id)
                    filter1_mock = Mock()
                    join_mock.filter.return_value = filter1_mock

                    # Mock second .filter(GoogleCalendarEvent.connection_id == source_connection.id)
                    filter2_mock = Mock()
                    filter1_mock.filter.return_value = filter2_mock

                    # Mock .all() to return our lessons list
                    filter2_mock.all.return_value = [lesson]  # Return a REAL list, not a Mock

                    return lesson_query_mock
                else:
                    # For User query or others
                    print(f"      Returning generic Mock for {query_type}")
                    return Mock()
            elif call_num >= 2:
                # Inner session - handle lesson and event queries for processing
                if query_num == 1:
                    # First query: get lesson to process (with for_update)
                    print("      Returning lesson to process query")
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = lesson
                    return lesson_query_mock
                elif query_num == 2:
                    # Second query: get event record (with for_update)
                    print("      Returning event record query")
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = event_record
                    return event_query_mock
                else:
                    return Mock()
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
            print("\nQuery log:")
            for call_num, query_num, query_type, args in query_log:
                print(f"  Call {call_num}, Query {query_num}: {query_type}")

            if result > 0:
                print("SUCCESS: Lesson was processed!")
            else:
                print("FAILURE: No lessons were processed")


if __name__ == "__main__":
    test_debug()