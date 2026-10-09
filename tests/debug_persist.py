#!/usr/bin/env python3
"""
Debug the _persist_google_events method directly.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import GoogleCalendarConnection


def test_persist_directly():
    """Test _persist_google_events directly with proper mocking."""
    print("Testing _persist_google_events directly...")

    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")

    # Create a mock connection
    conn = Mock()
    conn.id = 1
    conn.user_id = 1
    conn.calendar_id = "calendar1"
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

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Mock the query for GoogleCalendarEvent - this is what _persist_google_events uses
        # It queries: session.query(GoogleCalendarEvent).filter(
        #     GoogleCalendarEvent.connection_id == connection.id,
        #     GoogleCalendarEvent.google_event_id == event_id
        # ).first()

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
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_persist_directly()