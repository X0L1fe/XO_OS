#!/usr/bin/env python3
"""
Detailed debug script to see exactly what queries are being made in each session.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def debug_session_calls_detailed():
    """Debug what session calls are actually being made with detailed query tracking."""
    print("Debugging session calls (detailed)...")

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

    # Track session and query details
    session_details = []

    def session_mock(*args, **kwargs):
        session_index = len(session_details)
        session_details.append({
            'index': session_index,
            'queries': []
        })
        call_num = session_index + 1
        print(f"\n=== SESSION CALL #{call_num} ===")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        def query_side_effect(*query_args):
            query_index = len(session_details[session_index]['queries'])
            session_details[session_index]['queries'].append({
                'index': query_index,
                'args': query_args
            })
            query_num = query_index + 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])
            print(f"  Query #{query_num}: {query_type}")
            if len(query_args) > 1:
                print(f"    Args: {query_args[1:]}")

            # Handle different query types with proper returns
            if query_args[0] is User:
                # User query - return a mock user
                print(f"    -> Returning mock User (id={user_id}, selected_calendar_id={target_calendar_id})")
                user_mock = Mock()
                user_mock.id = user_id
                user_mock.selected_calendar_id = target_calendar_id  # Make it match target for relevance check
                mock_query = Mock()
                mock_query.first.return_value = user_mock
                return mock_query
            elif query_args[0] is GoogleCalendarConnection:
                # Connection query
                print(f"    -> Determining which connection to return")
                mock_query = Mock()
                # We need to figure out if this is source or target connection check
                # Let's look at the session and query context
                current_session_idx = session_index
                current_query_idx = query_index

                print(f"    Context: session={current_session_idx}, query={current_query_idx}")

                # Simplified logic: return source for first connection query, target for second
                if current_query_idx == 0:  # First connection query in this session
                    print(f"    -> Returning source connection")
                    mock_query.first.return_value = source_connection
                elif current_query_idx == 1:  # Second connection query in this session
                    print(f"    -> Returning target connection")
                    mock_query.first.return_value = target_connection
                else:
                    print(f"    -> Returning source connection (default)")
                    mock_query.first.return_value = source_connection
                return mock_query
            elif query_args[0] is Lesson:
                # Lesson query - for the complex join
                print(f"    -> Returning mock Lesson query (will chain for join+filter+filter+all)")
                mock_query = Mock()
                mock_query.join.return_value = mock_query  # For chaining: .join()
                mock_query.filter.return_value = mock_query  # For chaining: .filter()
                mock_query.filter.return_value = mock_query  # For chaining: .filter() (second one)
                mock_query.all.return_value = [test_lesson]  # For .all(): return our lesson
                return mock_query
            else:
                # Default fallback for other query types
                print(f"    -> Returning generic mock (chaining enabled)")
                mock_query = Mock()
                mock_query.join.return_value = mock_query
                mock_query.filter.return_value = mock_query
                mock_query.all.return_value = []
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
                print(f"Total session calls: {len(session_details)}")

                # Print detailed breakdown
                for i, session in enumerate(session_details):
                    print(f"\nSession #{i+1} had {len(session['queries'])} queries:")
                    for j, query in enumerate(session['queries']):
                        query_type = query['args'][0].__name__ if hasattr(query['args'][0], '__name__') else str(query['args'][0])
                        print(f"  Query #{j+1}: {query_type}")

            except Exception as e:
                print(f"\nException: {e}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    debug_session_calls_detailed()