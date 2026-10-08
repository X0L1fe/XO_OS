#!/usr/bin/env python3
"""
Run just the cancellation test to see what happens.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_cancellation_isolation_between_calendars():
    """Test that cancelled events in one calendar don't affect lessons in another."""
    print("Test: Cancellation isolation between calendars")

    db = Database()
    service1 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")
    service2 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar2")

    # Two connections
    conn1 = Mock()
    conn1.id = 1
    conn1.user_id = 1
    conn1.calendar_id = "calendar1"
    conn1.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    conn2 = Mock()
    conn2.id = 2
    conn2.user_id = 1
    conn2.calendar_id = "calendar2"
    conn2.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    # Different google_event_id for each calendar (more realistic)
    event_id_1 = "event_calendar1_123"
    event_id_2 = "event_calendar2_456"

    # Lessons for each connection
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.user_id = 1
    lesson1.google_event_id = event_id_1
    lesson1.subject = "Lesson for Calendar 1"

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.user_id = 1
    lesson2.google_event_id = event_id_2
    lesson2.subject = "Lesson for Calendar 2"

    # GoogleCalendarEvent links
    gcal_event1 = Mock()
    gcal_event1.connection_id = conn1.id
    gcal_event1.google_event_id = event_id_1

    gcal_event2 = Mock()
    gcal_event2.connection_id = conn2.id
    gcal_event2.google_event_id = event_id_2

    # Cancelled event from Google Calendar FOR CALENDAR 1
    cancelled_event_calendar1 = {
        "id": event_id_1,
        "status": "cancelled",
        "summary": "Cancelled Event from Calendar 1"
    }

    # Cancelled event from Google Calendar FOR CALENDAR 2
    cancelled_event_calendar2 = {
        "id": event_id_2,
        "status": "cancelled",
        "summary": "Cancelled Event from Calendar 2"
    }

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Setup for service1 - should clear lesson1 (event is from calendar1)
        # No need to mock connection query because the function receives the connection object

        # Setup lesson query for service1
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = [lesson1]  # Only lesson1 for connection 1
        mock_session.query.return_value = lesson_query_mock

        try:
            service1._handle_cancelled_google_events(conn1, [cancelled_event_calendar1], mock_session)
            # Lesson1's google_event_id should BE cleared
            assert lesson1.google_event_id is None
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson1 cleared")
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service1: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()

        # Setup for service2 - should clear lesson2 (event is from calendar2)
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = [lesson2]  # Only lesson2 for connection 2
        mock_session.query.return_value = lesson_query_mock

        try:
            service2._handle_cancelled_google_events(conn2, [cancelled_event_calendar2], mock_session)
            # Lesson2's google_event_id should BE cleared
            assert lesson2.google_event_id is None
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson2 cleared")
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service2: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()

        # Setup for service1 - should NOT clear lesson2 (event is from calendar2, not calendar1)
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []  # No lessons for connection 1 with event_id_2
        mock_session.query.return_value = lesson_query_mock

        print(f"Before assertion: lesson1.google_event_id = {lesson1.google_event_id}")
        print(f"Expected: {event_id_1}")

        try:
            service1._handle_cancelled_google_events(conn1, [cancelled_event_calendar2], mock_session)
            # Lesson2's google_event_id should NOT be cleared (it's not lesson1's event)
            assert lesson1.google_event_id == event_id_1
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson1 unaffected by calendar2's event")
        except AssertionError as e:
            print(f"  [FAILURE] Assertion failed: lesson1.google_event_id = {lesson1.google_event_id}, expected = {event_id_1}")
            raise
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service1: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()

        # Setup for service2 - should NOT clear lesson1 (event is from calendar1, not calendar2)
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []  # No lessons for connection 2 with event_id_1
        mock_session.query.return_value = lesson_query_mock

        try:
            service2._handle_cancelled_google_events(conn2, [cancelled_event_calendar1], mock_session)
            # Lesson1's google_event_id should NOT be cleared (it's not lesson2's event)
            assert lesson2.google_event_id == event_id_2
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson2 unaffected by calendar1's event")
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service2: {e}")
            raise

    print("  [PASS] Cancellation isolation between calendars test passed")


if __name__ == "__main__":
    print("Running cancellation isolation test...")
    print("=" * 50)
    try:
        test_cancellation_isolation_between_calendars()
        print("=" * 50)
        print("Test passed!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)