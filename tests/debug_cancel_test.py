#!/usr/bin/env python3
"""
Debug test for _handle_cancelled_google_events method.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database


def test_handle_cancelled_debug():
    """Debug the _handle_cancelled_google_events method."""
    print("Debugging _handle_cancelled_google_events...")

    db = Database()
    service = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")

    # Mock connection
    mock_conn = Mock()
    mock_conn.id = 1
    mock_conn.user_id = 1
    mock_conn.calendar_id = "calendar1"
    mock_conn.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    # Test event - this is for OTHER calendar
    test_event = {
        "id": "event_other_calendar",
        "status": "cancelled",
        "summary": "Cancelled Event"
    }

    # Lesson that belongs to THIS calendar
    lesson_mine = Mock()
    lesson_mine.id = 101
    lesson_mine.user_id = 1
    lesson_mine.google_event_id = "my_event"
    lesson_mine.subject = "My Lesson"

    # Mock the database session
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Setup the query to return our lesson (simulating it belongs to this connection)
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = [lesson_mine]  # Our lesson is returned
        mock_session.query.return_value = lesson_query_mock

        print(f"Before: lesson_mine.google_event_id = {lesson_mine.google_event_id}")

        try:
            service._handle_cancelled_google_events(mock_conn, [test_event], mock_session)
            print(f"After: lesson_mine.google_event_id = {lesson_mine.google_event_id}")

            if lesson_mine.google_event_id is None:
                print("  [RESULT] Lesson was cleared (unexpected)")
            else:
                print("  [RESULT] Lesson was not cleared (expected)")
        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    test_handle_cancelled_debug()