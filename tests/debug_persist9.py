#!/usr/bin/env python3
"""
Debug the _persist_google_events method with correct mock setup for combined filters.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService, _parse_google_date_or_datetime
from app.database.db import Database
from app.database.models import GoogleCalendarConnection


def test_persist_with_combined_filters():
    """Test _persist_google_events with correct mock setup for combined filters."""
    print("Testing _persist_google_events with combined filters mock setup...")

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

        # Create mocks for the correct chain:
        # session.query(GoogleCalendarEvent) -> query_mock
        # query_mock.filter(connection_condition, event_condition) -> filter_mock
        # filter_mock.first() -> existing_event (None for new event)

        query_mock = Mock()
        filter_mock = Mock()

        # Set up the chain with proper tracking
        def track_query_return(*args, **kwargs):
            print(f"    session.query({args[0] if args else 'no args'}) called -> returning query_mock")
            return query_mock

        def track_query_filter_return(*args, **kwargs):
            print(f"    query_mock.filter({len(args)} conditions) called -> returning filter_mock")
            return filter_mock

        def track_filter_first_return(*args, **kwargs):
            print(f"    filter_mock.first() called -> returning None (new event)")
            return None

        # Apply the tracking
        mock_session.query.side_effect = track_query_return
        query_mock.filter.side_effect = track_query_filter_return
        filter_mock.first.side_effect = track_filter_first_return

        # Also let's track what gets added
        added_items = []
        def track_add(item):
            added_items.append(item)
            print(f"  TRACKED ADD: Adding item of type {type(item)}")
            if hasattr(item, 'google_event_id'):
                print(f"    google_event_id: {item.google_event_id}")

        mock_session.add.side_effect = track_add

        print("Calling _persist_google_events...")
        try:
            service._persist_google_events(conn, [test_event])
            print(f"\nResults:")
            print(f"  mock_session.add called: {mock_session.add.called}")
            print(f"  Number of items tracked as added: {len(added_items)}")

            if mock_session.add.called or len(added_items) > 0:
                print("  [SUCCESS] add was called or items were tracked")
            else:
                print("  [FAILURE] add was NOT called and no items tracked")

        except Exception as e:
            print(f"  [ERROR] Exception: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_persist_with_combined_filters()