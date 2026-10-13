#!/usr/bin/env python3
"""
Debug script to trace the full flow of switch_calendar_for_user.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def debug_full_flow():
    """Debug the full flow of switch_calendar_for_user."""
    print("Debugging full flow...")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    print(f"source_calendar_id: '{source_calendar_id}'")
    print(f"target_calendar_id: '{target_calendar_id}'")

    # Create simple mock objects
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

    # Session mock to trace everything
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

            # Handle different query types in order
            if query_args[0] is User:
                # User query - this happens first in the session
                print(f"    -> Processing User query")
                user_mock = Mock()
                user_mock.id = user_id
                user_mock.selected_calendar_id = target_calendar_id  # Match target for relevance check

                # Show what the relevance check will do
                relevance_check = user_mock.selected_calendar_id != target_calendar_id
                print(f"    -> User selected_calendar_id: '{user_mock.selected_calendar_id}'")
                print(f"    -> Target calendar_id: '{target_calendar_id}'")
                print(f"    -> Relevance check (selected != target): {relevance_check}")

                mock_query = Mock()
                mock_query.first.return_value = user_mock
                return mock_query

            elif query_args[0] is GoogleCalendarConnection:
                # Connection queries - these happen after User query
                print(f"    -> Processing GoogleCalendarConnection query")

                # We need to determine if this is source or target connection check
                # Based on the order in the code: source first, then target

                if query_count == 1:
                    # This would be the FIRST GoogleCalendarConnection query in this session
                    # Which should be the source connection check
                    print(f"    -> This appears to be source connection check (1st GCC query)")
                    mock_query = Mock()
                    mock_query.first.return_value = source_connection
                    print(f"    -> Returning source_connection: {source_connection is not None}")
                    return mock_query
                elif query_count == 2:
                    # This would be the SECOND GoogleCalendarConnection query in this session
                    # Which should be the target connection check
                    print(f"    -> This appears to be target connection check (2nd GCC query)")
                    mock_query = Mock()
                    mock_query.first.return_value = target_connection
                    print(f"    -> Returning target_connection: {target_connection is not None}")
                    return mock_query
                else:
                    # Any additional connection queries
                    print(f"    -> Additional connection query (#{query_count}), returning source as default")
                    mock_query = Mock()
                    mock_query.first.return_value = source_connection
                    return mock_query

            elif query_args[0] is Lesson:
                # Lesson queries happen later (in separate sessions for processing lessons)
                print(f"    -> Processing Lesson query")
                mock_query = Mock()
                mock_query.join.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.all.return_value = [test_lesson]
                return mock_query

            else:
                # Fallback for any other query types
                print(f"    -> Processing other query type, returning generic mock")
                mock_query = Mock()
                mock_query.join.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.all.return_value = []
                mock_query.first.return_value = None
                mock_query.with_for_update.return_value = mock_query
                return mock_query

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Service mock
    def get_service_mock(*args, **kwargs):
        print(f"  SERVICE CALL - This happens during lesson processing")
        mock_service = Mock()
        mock_service.events = Mock(return_value=Mock())
        mock_service.events().get = Mock(return_value=Mock())
        mock_service.events().get().execute = Mock(return_value={"id": "event_123"})
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
                print(f"\nFinal Result: {result}")
                print(f"Total session calls: {session_call_count}")
            except Exception as e:
                print(f"\nException: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    debug_full_flow()