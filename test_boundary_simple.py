#!/usr/bin/env python3
"""
Test script to verify the connection boundary functionality.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService, _parse_google_date_or_datetime
from app.database.db import Database

def test_is_event_created_after_connection():
    """Test the boundary check function."""
    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Test case 1: event created after connection -> should return True
    event_after = {"id": "event1", "created": "2026-10-08T12:00:00Z"}
    connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)
    result = service._is_event_created_after_connection(event_after, connected_at)
    assert result == True, f"Expected True, got {result}"

    # Test case 2: event created before connection -> should return False
    event_before = {"id": "event2", "created": "2026-10-06T12:00:00Z"}
    result = service._is_event_created_after_connection(event_before, connected_at)
    assert result == False, f"Expected False, got {result}"

    # Test case 3: event created at connection time -> should return True (inclusive)
    event_at = {"id": "event3", "created": "2026-10-07T12:00:00Z"}
    result = service._is_event_created_after_connection(event_at, connected_at)
    assert result == True, f"Expected True, got {result}"

    # Test case 4: event with missing created -> should return False
    event_no_created = {"id": "event4"}
    result = service._is_event_created_after_connection(event_no_created, connected_at)
    assert result == False, f"Expected False, got {result}"

    # Test case 5: event with malformed created -> should return False
    event_bad_created = {"id": "event5", "created": "not-a-date"}
    result = service._is_event_created_after_connection(event_bad_created, connected_at)
    assert result == False, f"Expected False, got {result}"

    print("All boundary check tests passed!")

def test_persist_respects_boundary():
    """Test that _persist_google_events respects the boundary."""
    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Mock the database session
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session

        # Mock connection query
        mock_conn = Mock()
        mock_conn.id = 1
        mock_conn.user_id = 1
        mock_conn.calendar_id = "primary"
        mock_conn.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_conn

        # Mock the GoogleCalendarEvent query to return None (new event)
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Test event that should be persisted (after connection)
        event_after = {
            "id": "event_after_123",
            "summary": "Test Event After Connection",
            "start": {"dateTime": "2026-10-08T19:00:00Z"},
            "end": {"dateTime": "2026-10-08T20:00:00Z"},
            "created": "2026-10-08T12:00:00Z",  # After connection
            "updated": "2026-10-08T12:00:00Z",
            "status": "confirmed"
        }

        # Test event that should be skipped (before connection)
        event_before = {
            "id": "event_before_456",
            "summary": "Test Event Before Connection",
            "start": {"dateTime": "2026-10-06T19:00:00Z"},
            "end": {"dateTime": "2026-10-06T20:00:00Z"},
            "created": "2026-10-06T12:00:00Z",  # Before connection
            "updated": "2026-10-06T12:00:00Z",
            "status": "confirmed"
        }

        # This should not throw an exception
        try:
            service._persist_google_events(mock_conn, [event_after, event_before], mock_session)
            # Check that add was called only once (for the after event)
            assert mock_session.add.call_count == 1
            # Check that the added event has the correct ID
            added_event = mock_session.add.call_args[0][0]
            assert added_event.google_event_id == "event_after_123"
            print("Persistence boundary test passed!")
        except Exception as e:
            print(f"Persistence boundary test failed: {e}")
            raise

if __name__ == "__main__":
    print("Testing connection boundary implementation...")
    print("=" * 50)

    test_is_event_created_after_connection()
    test_persist_respects_boundary()

    print("=" * 50)
    print("All tests passed!")