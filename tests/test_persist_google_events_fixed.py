#!/usr/bin/env python3
"""
Focused test for _persist_google_events method signature fix.
"""

import os
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.db import Database
from app.google_calendar.service import GoogleCalendarSyncService


def test_persist_google_events_signature():
    """Test that _persist_google_events accepts session as optional argument."""
    print("Testing _persist_google_events method signature...")

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
        "status": "confirmed",
    }

    # Test 1: Call with only connection and google_events (should create internal session)
    with patch.object(db, "session") as mock_session_method:
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
            print(
                "  [OK] _persist_google_events called successfully with 2 args (self + connection, google_events)"
            )
            # Check that the internal session's add was called
            assert mock_session.add.called
        except Exception as e:
            print(f"  [FAIL] _persist_google_events threw exception: {e}")
            raise

    # Test 2: Call with connection, google_events, and an external session (should use that session)
    with patch.object(db, "session") as mock_session_method:
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
            # Pass the mock session as the third argument
            service._persist_google_events(mock_conn, [test_event], mock_session)
            print(
                "  [OK] _persist_google_events called successfully with 3 args (self + connection, google_events, session)"
            )
            # Check that the provided session's add was called
            assert mock_session.add.called
        except Exception as e:
            print(f"  [FAIL] _persist_google_events threw exception: {e}")
            raise

    # Test 3: Ensure that calling with no google_events does not crash
    with patch.object(db, "session") as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        mock_query = Mock()
        mock_filter = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        try:
            service._persist_google_events(mock_conn, [], mock_session)
            print("  [OK] _persist_google_events called with empty event list")
        except Exception as e:
            print(
                f"  [FAIL] _persist_google_events threw exception with empty list: {e}"
            )
            raise


if __name__ == "__main__":
    print("Testing _persist_google_events signature fix...")
    print("=" * 50)

    try:
        test_persist_google_events_signature()
        print("=" * 50)
        print("All tests passed! [OK]")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
