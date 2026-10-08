#!/usr/bin/env python3
"""
Debug the _persist_google_events method with detailed parsing checks.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService, _parse_google_date_or_datetime
from app.database.db import Database
from app.database.models import GoogleCalendarConnection


def test_persist_with_detailed_debug():
    """Test _persist_google_events with detailed debugging."""
    print("Testing _persist_google_events with detailed debugging...")

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

    # Test the _is_event_created_after_connection method directly
    is_created_after = service._is_event_created_after_connection(test_event, conn.connected_at)
    print(f"_is_event_created_after_connection returned: {is_created_after}")

    if not is_created_after:
        print("Event would be skipped due to connection boundary check")
        return

    # Debug the parsing steps
    start_info = test_event.get("start", {})
    end_info = test_event.get("end", {})
    print(f"start_info: {start_info}")
    print(f"end_info: {end_info}")

    is_all_day = "date" in start_info and "date" in end_info
    print(f"is_all_day: {is_all_day}")

    start_time = _parse_google_date_or_datetime(start_info.get("dateTime") or start_info.get("date"))
    end_time = _parse_google_date_or_datetime(end_info.get("dateTime") or end_info.get("date"))
    created_at_google = _parse_google_date_or_datetime(test_event.get("created"))
    updated_at_google = _parse_google_date_or_datetime(test_event.get("updated"))
    original_start_time = _parse_google_date_or_datetime(test_event.get("originalStartTime"))

    print(f"start_time: {start_time}")
    print(f"end_time: {end_time}")
    print(f"created_at_google: {created_at_google}")
    print(f"updated_at_google: {updated_at_google}")
    print(f"original_start_time: {original_start_time}")

    if start_time is None or end_time is None:
        print("ERROR: start_time or end_time is None - would skip event!")
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

        # Also let's track what gets added
        added_items = []
        def track_add(item):
            added_items.append(item)
            print(f"  TRACKED: Adding item of type {type(item)}")

        mock_session.add.side_effect = track_add

        print("Calling _persist_google_events...")
        try:
            service._persist_google_events(conn, [test_event])
            print(f"mock_session.add called: {mock_session.add.called}")
            print(f"Number of items tracked as added: {len(added_items)}")
            if mock_session.add.called or len(added_items) > 0:
                print("  [SUCCESS] add was called or items were tracked")
                if added_items:
                    print(f"  First added item: {added_items[0]}")
                    print(f"  Type of first added item: {type(added_items[0])}")
            else:
                print("  [FAILURE] add was NOT called and no items tracked")
        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_persist_with_detailed_debug()