#!/usr/bin/env python3
"""
Debug the connection object passing.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database


def test_connection_passing():
    """Test that the connection object is passed correctly."""
    print("Testing connection object passing...")

    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")

    # Create a mock connection with REAL datetime objects
    conn = Mock()
    conn.id = 1
    conn.user_id = 1
    conn.calendar_id = "calendar1"
    # Use a REAL datetime, not a Mock
    conn.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    print(f"Original conn.connected_at: {conn.connected_at}")
    print(f"Type: {type(conn.connected_at)}")

    # Let's manually call _is_event_created_after_connection to see what happens
    test_event = {
        "id": "test_event_123",
        "summary": "Test Event",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed"
    }

    try:
        result = service._is_event_created_after_connection(test_event, conn)
        print(f"_is_event_created_after_connection result: {result}")
    except Exception as e:
        print(f"Error in _is_event_created_after_connection: {e}")
        import traceback
        traceback.print_exc()

    # Now let's see what happens when we call _persist_google_events
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Mock the query for GoogleCalendarEvent to return None (new event)
        query_mock = Mock()
        filter_mock1 = Mock()
        filter_mock2 = Mock()
        mock_session.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock1
        filter_mock1.filter.return_value = filter_mock2
        filter_mock2.first.return_value = None

        print("\nCalling _persist_google_events...")
        try:
            service._persist_google_events(conn, [test_event])
            print(f"Success! mock_session.add called: {mock_session.add.called}")
        except Exception as e:
            print(f"Error in _persist_google_events: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_connection_passing()