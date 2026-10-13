#!/usr/bin/env python3
"""
Simple test to see how many times session_mock is called.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User


def test_simple_session_calls():
    """Simple test to count session calls."""
    print("=== Simple Session Call Counting ===")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    call_count = 0

    def session_mock(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        print(f"SESSION_MOCK CALLED #{call_count}")
        print(f"  Args: {args}")
        print(f"  Kwargs: {kwargs}")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        # Very simple mock that just returns None for everything
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_query.all.return_value = []
        mock_query.join.return_value = mock_query
        mock_query.with_for_update.return_value = mock_query
        return mock_session

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        print("Calling switch_calendar_for_user...")
        try:
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )
            print(f"Result: {result}")
            print(f"Total session_mock calls: {call_count}")
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_simple_session_calls()