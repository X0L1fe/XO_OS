#!/usr/bin/env python3
"""Debug test for switch_calendar_for_user - attempt 2."""

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

    # Track session calls
    session_calls = []

    def session_mock(*args, **kwargs):
        session_calls.append(len(session_calls) + 1)
        call_num = len(session_calls)
        print(f"Session call #{call_num}")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        if call_num == 1:
            # Outer session - return connections and lessons
            print("  Setting up outer session")

            # We'll get multiple queries here - need to handle them properly
            query_counter = 0

            def query_side_effect(*args):
                nonlocal query_counter
                query_counter += 1
                print(f"    Outer session query #{query_counter} called with: {args}")

                if args[0] == GoogleCalendarConnection:
                    # This could be either source or target connection query
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    # First call: source connection, Second call: target connection
                    if query_counter == 1:
                        connection_filter_mock.first.return_value = source_connection
                    elif query_counter == 2:
                        connection_filter_mock.first.return_value = target_connection
                    else:
                        connection_filter_mock.first.return_value = None  # Shouldn't happen
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif args[0] == Lesson:
                    # This is the lessons query with join
                    lesson_query_mock = Mock()
                    # We need to mock the join and subsequent filters
                    join_mock = Mock()
                    lesson_query_mock.join.return_value = join_mock

                    # Filter for Lesson.user_id == user_id
                    filter1_mock = Mock()
                    join_mock.filter.return_value = filter1_mock
                    filter1_mock.filter.return_value = filter1_mock  # Self-reference for chaining

                    # Filter for GoogleCalendarEvent.connection_id == source_connection.id
                    filter2_mock = Mock()
                    filter1_mock.filter.return_value = filter2_mock
                    filter2_mock.filter.return_value = filter2_mock  # Self-reference for chaining

                    # .all() should return our lessons list
                    filter2_mock.all.return_value = [lesson]

                    return lesson_query_mock
                else:
                    # For any other query (like User query that was happening before)
                    return Mock()

            mock_session.query.side_effect = query_side_effect

        elif call_num >= 2:
            # Inner session - return lesson and event for processing
            print(f"  Setting up inner session #{call_num}")

            # For inner sessions, we expect:
            # 1. Query for Lesson with for_update to get the lesson to process
            # 2. Query for GoogleCalendarEvent with for_update to get the event record

            inner_query_counter = 0

            def query_side_effect(*args):
                nonlocal inner_query_counter
                inner_query_counter += 1
                print(f"    Inner session #{call_num} query #{inner_query_counter} called with: {args}")

                if args[0] == Lesson:
                    # Query for lesson with for_update
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock

                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = lesson  # Return our lesson

                    return lesson_query_mock
                elif args[0] == GoogleCalendarEvent:
                    # Query for event record with for_update
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock

                    # We need to filter by connection_id and google_event_id
                    # Let's just return our event record for simplicity
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = event_record  # Return our event record

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
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(return_value=source_event)

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)

            print("  Returning source service")
        else:
            # Target service
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(return_value=created_event)

            print("  Returning target service")
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
            print(f"Session calls: {session_calls}")
            print(f"Service calls: {service_calls}")

            if result > 0:
                print("SUCCESS: Lesson was processed!")
            else:
                print("FAILURE: No lessons were processed")


if __name__ == "__main__":
    test_debug()