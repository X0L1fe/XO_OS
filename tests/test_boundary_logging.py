#!/usr/bin/env python3
"""
Test script to verify the boundary logging functionality.
"""

import sys
import os
import logging
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

def test_boundary_logging():
    """Test that events skipped due to boundary are logged."""
    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Set up logging to capture log messages
    log_capture = []
    class LogHandler(logging.Handler):
        def emit(self, record):
            log_capture.append(self.format(record))

    logger = logging.getLogger('app.google_calendar.service')
    logger.setLevel(logging.INFO)
    handler = LogHandler()
    logger.addHandler(handler)

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
            service._persist_google_events(mock_conn, [event_before], mock_session)
            # Check that no add was called (event should be skipped)
            assert mock_session.add.call_count == 0

            # Check that we got a log message
            assert len(log_capture) > 0
            log_message = log_capture[0]
            assert "Skipping Google Calendar event due to connection boundary" in log_message
            assert "connection_id=1" in log_message
            assert "calendar_id=primary" in log_message
            assert "google_event_id=event_before_456" in log_message
            assert "event.created=2026-10-06T12:00:00Z" in log_message
            assert "reason=\"created_before_connection\"" in log_message

            print("Boundary logging test passed!")
        except Exception as e:
            print(f"Boundary logging test failed: {e}")
            raise
        finally:
            logger.removeHandler(handler)

if __name__ == "__main__":
    print("Testing connection boundary logging...")
    print("=" * 50)

    test_boundary_logging()

    print("=" * 50)
    print("All tests passed!")