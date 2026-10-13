#!/usr/bin/env python3
"""
Test the user query specifically - fixed version 2.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User


def test_user_query():
    """Test just the user query part."""
    print("Testing user query...")

    db = Database()
    user_id = 1
    target_calendar_id = "target_calendar_id"

    # Simple session mock for just the user query
    def session_mock(*args, **kwargs):
        print(f"  Session call")
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        def query_side_effect(*query_args):
            print(f"    Query called with: {query_args}")
            if query_args[0] is User:
                print(f"    -> User query")
                # Create a user mock that returns actual values when attributes are accessed
                user_mock = Mock()
                user_mock.id = user_id
                # Configure the mock to return the actual string when selected_calendar_id is accessed
                type(user_mock).selected_calendar_id = Mock(return_value=target_calendar_id)
                # Actually, let's just set it directly - Mock will return the value we set
                user_mock.selected_calendar_id = target_calendar_id
                mock_query = Mock()
                mock_query.first.return_value = user_mock
                print(f"    -> Returning user_mock: {user_mock}")
                print(f"    -> user_mock is None: {user_mock is None}")
                print(f"    -> bool(user_mock): {bool(user_mock)}")
                print(f"    -> user_mock.selected_calendar_id: {user_mock.selected_calendar_id}")
                print(f"    -> type(user_mock.selected_calendar_id): {type(user_mock.selected_calendar_id)}")
                return mock_query
            else:
                print(f"    -> Non-User query")
                mock_query = Mock()
                mock_query.first.return_value = None
                return mock_query

        mock_session.query.side_effect = query_side_effect
        return mock_session

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        # Test the exact snippet from the service
        print("Testing: user = session.query(User).filter(User.id == user_id).first()")
        with db.session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            print(f"Returned user: {user}")
            print(f"User is None: {user is None}")
            if user:
                print(f"User ID: {getattr(user, 'id', 'NO ID ATTR')}")
                selected_cal_id = getattr(user, 'selected_calendar_id', 'NO SELECTED_CALENDAR_ID ATTR')
                print(f"Selected calendar ID: {selected_cal_id}")
                print(f"Type of selected_calendar_id: {type(selected_cal_id)}")

                # Test the relevance check
                relevance_check = selected_cal_id != target_calendar_id
                print(f"Relevance check (selected != target): {relevance_check}")
                print(f"Should return 0: {relevance_check}")


if __name__ == "__main__":
    test_user_query()