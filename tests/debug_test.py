#!/usr/bin/env python3
"""Debug test for switch_calendar_for_user."""

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

            # Query for connections
            connection_query_mock = Mock()
            connection_filter_mock = Mock()
            connection_filter_mock.first.side_effect = [source_connection, target_connection]
            connection_query_mock.filter.return_value = connection_filter_mock

            # Query for lessons (joining with GoogleCalendarEvent)
            lesson_join_mock = Mock()
            lesson_filter_mock1 = Mock()
            lesson_filter_mock2 = Mock()
            lesson_filter_mock3 = Mock()
            lesson_join_mock.filter.return_value = lesson_filter_mock1
            lesson_filter_mock1.filter.return_value = lesson_filter_mock2
            lesson_filter_mock2.filter.return_value = lesson_filter_mock3
            lesson_filter_mock3.all.return_value = [lesson]

            lesson_query_mock = Mock()
            lesson_query_mock.join.return_value = lesson_join_mock

            def query_side_effect(*args):
                print(f"    Outer session query called with: {args}")
                if args[0] == GoogleCalendarConnection:
                    return connection_query_mock
                elif args[0] == Lesson:
                    return lesson_query_mock
                else:
                    return Mock()

            mock_session.query.side_effect = query_side_effect

        elif call_num >= 2:
            # Inner session - return lesson and event for processing
            print(f"  Setting up inner session #{call_num}")

            # For the lesson query (with for_update)
            lesson_to_process_mock = Mock()
            lesson_to_process_mock.id = lesson.id
            lesson_to_process_mock.user_id = lesson.user_id
            lesson_to_process_mock.google_event_id = lesson.google_event_id
            lesson_to_process_mock.subject = lesson.subject
            lesson_to_process_mock.start_time = lesson.start_time
            lesson_to_process_mock.end_time = lesson.end_time

            # For the event record query
            event_record_mock = Mock()
            event_record_mock.id = event_record.id
            event_record_mock.connection_id = source_connection.id
            event_record_mock.google_event_id = lesson.google_event_id
            event_record_mock.calendar_id = source_calendar_id
            event_record_mock.summary = event_record.summary
            event_record_mock.start_time = event_record.start_time
            event_record_mock.end_time = event_record.end_time

            def query_side_effect(*args):
                print(f"    Inner session #{call_num} query called with: {args}")
                if args[0] == Lesson:
                    lesson_query_mock_inner = Mock()
                    # Simulate .filter(Lesson.id == lesson.id).with_for_update().first()
                    filter_mock = Mock()
                    filter_mock.first.return_value = lesson_to_process_mock
                    lesson_query_mock_inner.filter.return_value = filter_mock
                    return lesson_query_mock_inner
                elif args[0] == GoogleCalendarEvent:
                    event_query_mock_inner = Mock()
                    # Simulate .filter(...).with_for_update().first()
                    filter_mock = Mock()
                    filter_mock.first.return_value = event_record_mock
                    event_query_mock_inner.filter.return_value = filter_mock
                    return event_query_mock_inner
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
            mock_service.events().get().execute.return_value = source_event
            mock_service.events().delete().execute.return_value = None
            print("  Returning source service")
        else:
            # Target service
            mock_service.events().insert().execute.return_value = created_event
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


if __name__ == "__main__":
    test_debug()