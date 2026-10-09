#!/usr/bin/env python3
"""
Debug the _persist_google_events method with correct parameter passing.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import GoogleCalendarConnection


def test_persist_with_correct_params():
    """Test _persist_google_events with correct parameter passing."""
    print("Testing _persist_google_events with correct parameter passing...")

    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")

    # Create a mock connection with REAL datetime objects
    conn = Mock()
    conn.id = 1
    conn.user_id = 1
    conn.calendar_id = "calendar1"
    # Use a REAL datetime, not a Mock
    conn.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    # Test event
    test_event = {
        "id": "test_event_123",
        "summary": "Test Event",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed"
    }

    print(f"Event created time: {test_event['created']}")
    print(f"Connection connected_at: {conn.connected_at}")

    # Test the _is_event_created_after_connection method directly with corr
    is_created_after = service._is_event_created_after_connection(test_event, conn.connected_at)
    print(f"_is_event_created_after_connection returned: {is_created_after}")

    if not is_created_after:
        print("Event would be skipped due to connection boundary check")
        return

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Mock the query for GoogleCalendarEvent
        query_mock = Mock()
        filter_mock1 = Mock()
        filter_mock2 = Mock()

        # Set up the chain: query -> filter -> filter -> first
        mock_session.query.return_value = query_mock
        query_mock.filter.return_value = filter_mock1
        filter_mock1.filter.return_value = filter_mock2
        filter_mock2.first.return_value = None  # No existing event (should create new)

        print("Calling _persist_google_events...")
        try:
            service._persist_google_events(conn, [test_event])
            print(f"mock_session.add called: {mock_session.add.called}")
            if mock_session.add.called:
                print("  [SUCCESS] add was called")
                # Check what was added
                call_args = mock_session.add.call_args
                print(f"  Added object: {call_args[0][0] if call_args else 'None'}")
            else:
                print("  [FAILURE] add was NOT called")
                # Let's see what queries were made
                print(f"mock_session.query called: {mock_session.query.called}")
                if mock_session.query.called:
                    print(f"  query call count: {mock_session.query.call_count}")
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_persist_with_correct_params()