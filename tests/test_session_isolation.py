#!/usr/bin/env python3
"""
Test session isolation to understand how many times session_mock is called.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User


def test_session_isolation():
    """Test how session isolation works."""
    print("=== Testing Session Isolation ===")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Track session creation
    session_instances = []
    session_call_log = []

    def session_mock(*args, **kwargs):
        session_id = len(session_instances)
        session_instances.append(len(session_instances))  # Just append a marker
        call_number = len(session_instances)
        session_call_log.append(f"Session #{call_number} created")
        print(f"\n>>> SESSION MOCK CALL #{call_number} <<<")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_count = 0

        def query_side_effect(*query_args):
            nonlocal query_count
            query_count += 1
            query_type = query_args[0].__name__ if hasattr(query_args[0], '__name__') else str(query_args[0])
            print(f"    Session #{call_number}, Query #{query_count}: {query_type}")

            if query_args[0] is User:
                print(f"      -> User query")
                user_mock = Mock()
                user_mock.id = user_id
                user_mock.selected_calendar_id = target_calendar_id  # Match target

                # Properly chain the mock: query.filter().first()
                query_mock = Mock()
                filter_mock = Mock()
                query_mock.filter.return_value = filter_mock
                filter_mock.first.return_value = user_mock
                return query_mock
            else:
                print(f"      -> Non-User query (returning empty chain)")
                # Return a mock that allows chaining but returns None/empty
                query_mock = Mock()
                filter_mock = Mock()
                query_mock.filter.return_value = filter_mock
                filter_mock.first.return_value = None
                query_mock.all.return_value = []
                query_mock.join.return_value = query_mock
                return query_mock

        mock_session.query.side_effect = query_side_effect
        return mock_session

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        print("Calling switch_calendar_for_user...")
        try:
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )
            print(f"\n=== RESULTS ===")
            print(f"Return value: {result}")
            print(f"Number of session mock calls: {len(session_instances)}")
            print("Session call log:")
            for i, log in enumerate(session_call_log):
                print(f"  {i+1}. {log}")

        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_session_isolation()