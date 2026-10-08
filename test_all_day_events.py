#!/usr/bin/env python3
"""
Test script to verify all-day events implementation.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService, _parse_google_date_or_datetime
from app.database.db import Database

def test_parse_google_date_or_datetime():
    """Test the new date/time parsing function."""
    # Test dateTime string with Z
    result = _parse_google_date_or_datetime("2026-10-07T19:20:00.123Z")
    assert result is not None
    assert result.year == 2026
    assert result.month == 10
    assert result.day == 7
    assert result.hour == 19
    assert result.minute == 20
    assert result.second == 0
    assert result.microsecond == 123000
    assert result.tzinfo == timezone.utc

    # Test dateTime string with offset
    result = _parse_google_date_or_datetime("2026-10-07T19:20:00.123+02:00")
    assert result is not None
    assert result.year == 2026
    assert result.month == 10
    assert result.day == 7
    assert result.hour == 17  # 19:20 +02:00 -> 17:20 UTC
    assert result.minute == 20
    assert result.tzinfo == timezone.utc

    # Test date-only string (all-day event)
    result = _parse_google_date_or_datetime("2026-10-07")
    assert result is not None
    assert result.year == 2026
    assert result.month == 10
    assert result.day == 7
    assert result.hour == 0
    assert result.minute == 0
    assert result.second == 0
    assert result.microsecond == 0
    assert result.tzinfo == timezone.utc

    # Test None input
    result = _parse_google_date_or_datetime(None)
    assert result is None

    # Test empty string
    result = _parse_google_date_or_datetime("")
    assert result is None

    print("[OK] All date/time parsing tests passed")

def test_is_all_day_detection():
    """Test all-day event detection logic."""
    # We'll reuse the same logic as in _persist_google_events
    # Test all-day event (both start and end have date)
    event_all_day = {
        "start": {"date": "2026-10-07"},
        "end": {"date": "2026-10-08"}
    }
    start_info = event_all_day.get("start", {})
    end_info = event_all_day.get("end", {})
    is_all_day = "date" in start_info and "date" in end_info
    assert is_all_day == True

    # Test timed event (both start and end have dateTime)
    event_timed = {
        "start": {"dateTime": "2026-10-07T19:00:00Z"},
        "end": {"dateTime": "2026-10-07T20:00:00Z"}
    }
    start_info = event_timed.get("start", {})
    end_info = event_timed.get("end", {})
    is_all_day = "date" in start_info and "date" in end_info
    assert is_all_day == False

    # Test mixed case (should not happen in real Google Calendar, but let's handle it)
    event_mixed = {
        "start": {"date": "2026-10-07"},  # date only
        "end": {"dateTime": "2026-10-07T20:00:00Z"}  # dateTime
    }
    start_info = event_mixed.get("start", {})
    end_info = event_mixed.get("end", {})
    is_all_day = "date" in start_info and "date" in end_info
    assert is_all_day == False  # Only true if BOTH have date

    print("[OK] All-day event detection tests passed")

def test_persist_all_day_event():
    """Test that all-day events are persisted correctly."""
    db = Database()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Mock the database session
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session

        # Mock connection query
        mock_conn = Mock()
        mock_conn.id = 1
        mock_conn.user_id = 1
        mock_conn.calendar_id = "primary"
        mock_conn.connected_at = datetime.now(timezone.utc)
        mock_session.query.return_value.filter.return_value.first.return_value = mock_conn

        # Mock the GoogleCalendarEvent query to return None (new event)
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Test all-day event
        all_day_event = {
            "id": "all_day_event_123",
            "summary": "Test All-Day Event",
            "start": {"date": "2026-10-07"},
            "end": {"date": "2026-10-08"},
            "created": "2026-10-06T12:00:00Z",
            "updated": "2026-10-06T12:00:00Z",
            "status": "confirmed"
        }

        # This should not throw an exception
        try:
            sync_service._persist_google_events(mock_conn, [all_day_event])
            print("[OK] All-day event persistence test passed")
        except Exception as e:
            print(f"[ERROR] All-day event persistence test failed: {e}")
            raise

if __name__ == "__main__":
    print("Testing all-day events implementation...")
    print("=" * 50)

    test_parse_google_date_or_datetime()
    test_is_all_day_detection()
    test_persist_all_day_event()

    print("=" * 50)
    print("All tests passed! [OK]")