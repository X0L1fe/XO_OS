#!/usr/bin/env python3
"""
Debug script to see exactly what session calls are being made.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def debug_session_calls():
    """Debug what session calls are actually being made."""
    print("Debugging session calls...")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Create simple mock objects
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"

    test_event_record = GoogleCalendarEvent()
    test_event_record.id = 201
    test_event_record.connection_id = 1
    test_event_record.google_event_id = test_lesson.google_event_id
    test_event_record.calendar_id = source_calendar_id

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

    # Simple session mock that just counts and prints
    session_call_count = 0

    def session_mock(*args, **kwargs):
        nonlocal session_call_count
        session_call_count += 1
        call_num = session_call_count
        print(f"\n=== SESSION CALL #{call_num} ===")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_count = 0

        def query_side_effect(*query_args):
            nonlocal query_count
            query_count += 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])
            print(f"  Query #{query_count}: {query_type}")
            if len(query_args) > 1:
                print(f"    Args: {query_args[1:]}")

            # Return a basic mock that allows chaining
            mock_query = Mock()
            mock_query.join.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = []  # Default to empty list
            mock_query.first.return_value = None
            mock_query.with_for_update.return_value = mock_query
            return mock_query

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Simple service mock
    def get_service_mock(*args, **kwargs):
        print(f"  SERVICE CALL")
        mock_service = Mock()
        mock_service.events = Mock(return_value=Mock())
        mock_service.events().get = Mock(return_value=Mock())
        mock_service.events().get().execute = Mock(return_value={
            "id": "event_123",
            "summary": "Test Lesson",
            "start": {"dateTime": "2026-10-08T19:00:00Z"},
            "end": {"dateTime": "2026-10-08T20:00:00Z"},
        })
        mock_service.events().insert = Mock(return_value=Mock())
        mock_service.events().insert().execute = Mock(return_value={"id": "new_event_456"})
        mock_service.events().delete = Mock(return_value=Mock())
        mock_service.events().delete().execute = Mock(return_value=None)
        return mock_service

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            print("Calling switch_calendar_for_user...")
            try:
                result = GoogleCalendarSyncService.switch_calendar_for_user(
                    db, user_id, source_calendar_id, target_calendar_id
                )
                print(f"\nResult: {result}")
                print(f"Total session calls: {session_call_count}")
            except Exception as e:
                print(f"\nException: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    debug_session_calls()