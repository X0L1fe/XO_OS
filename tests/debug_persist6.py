#!/usr/bin/env python3
"""
Debug the _persist_google_events method with query call tracking.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService, _parse_google_date_or_datetime
from app.database.db import Database
from app.database.models import GoogleCalendarConnection


def test_persist_with_query_tracking():
    """Test _persist_google_events with query call tracking."""
    print("Testing _persist_google_events with query call tracking...")

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

    print(f"Event ID: {test_event['id']}")
    print(f"Connection ID: {conn.id}")

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Set up detailed tracking for the query chain
        query_call_count = 0
        filter_call_count = 0
        first_call_count = 0

        def track_query(*args, **kwargs):
            nonlocal query_call_count
            query_call_count += 1
            print(f"  QUERY called with args: {args}")
            query_mock = Mock()
            return query_mock

        def track_filter(*args, **kwargs):
            nonlocal filter_call_count
            filter_call_count += 1
            print(f"  FILTER called with args: {args}")
            filter_mock = Mock()
            return filter_mock

        def track_first(*args, **kwargs):
            nonlocal first_call_count
            first_call_count += 1
            print(f"  FIRST called")
            return None  # No existing event

        # Set up the mock chain
        query_mock = Mock()
        query_mock.filter = track_filter
        query_mock.first = track_first

        mock_session.query = track_query
        mock_session.query.return_value = query_mock

        # Also let's track what gets added
        added_items = []
        def track_add(item):
            added_items.append(item)
            print(f"  TRACKED ADD: Adding item of type {type(item)}")

        mock_session.add.side_effect = track_add

        print("Calling _persist_google_events...")
        try:
            service._persist_google_events(conn, [test_event])
            print(f"\nResults:")
            print(f"  mock_session.add called: {mock_session.add.called}")
            print(f"  Number of items tracked as added: {len(added_items)}")
            print(f"  Query call count: {query_call_count}")
            print(f"  Filter call count: {filter_call_count}")
            print(f"  First call count: {first_call_count}")

            if mock_session.add.called or len(added_items) > 0:
                print("  [SUCCESS] add was called or items were tracked")
            else:
                print("  [FAILURE] add was NOT called and no items tracked")

        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_persist_with_query_tracking()