#!/usr/bin/env python3
"""
Debug test for _persist_google_events method.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database


def test_persist_google_events_simple():
    """Simple test of _persist_google_events method."""
    print("Running simple _persist_google_events test...")

    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Mock connection
    mock_conn = Mock()
    mock_conn.id = 1
    mock_conn.user_id = 1
    mock_conn.calendar_id = "primary"
    mock_conn.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

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

    # Mock the database session
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Mock the query for existing event (return None to simulate new event)
        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        try:
            service._persist_google_events(mock_conn, [test_event])
            print("  [OK] _persist_google_events called successfully")
            # Check that the session's add was called
            if mock_session.add.called:
                print("  [OK] mock_session.add was called")
            else:
                print("  [FAIL] mock_session.add was NOT called")
                return False
        except Exception as e:
            print(f"  [FAIL] _persist_google_events threw exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    return True


if __name__ == "__main__":
    success = test_persist_google_events_simple()
    if success:
        print("\nAll tests passed!")
    else:
        print("\nTests failed!")
        sys.exit(1)