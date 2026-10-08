#!/usr/bin/env python3
"""
Debug test to see what's happening in the cancellation test.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def debug_cancellation_test():
    """Debug the cancellation test step by step."""
    print("Debugging cancellation test...")

    db = Database()
    service1 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")
    service2 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar2")

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

    event_id_1 = "event_calendar1_123"
    event_id_2 = "event_calendar2_456"

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

    # This is the failing case: service1 processing calendar2's cancelled event
    cancelled_event_calendar2 = {
        "id": event_id_2,
        "status": "cancelled",
        "summary": "Cancelled Event from Calendar 2"
    }

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        print(f"Before: lesson1.google_event_id = {lesson1.google_event_id}")

        # Setup for service1 - should NOT clear lesson2 (event is from calendar2, not calendar1)
        # Setup lesson query for service1: should return empty list (no lessons for conn1 with event_id_2)
        lesson_query_mock = Mock()
        join_mock = Mock()
        lesson_query_mock.join.return_value = join_mock
        filter_mock = Mock()
        join_mock.filter.return_value = filter_mock
        filter_mock.all.return_value = []  # No lessons for connection 1 with event_id_2
        mock_session.query.return_value = lesson_query_mock

        print("About to call service1._handle_cancelled_google_events")
        print(f"Mock setup: query -> lesson_query_mock")
        print(f"lesson_query_mock.join -> join_mock")
        print(f"join_mock.filter -> filter_mock")
        print(f"filter_mock.all -> []")

        try:
            service1._handle_cancelled_google_events(conn1, [cancelled_event_calendar2], mock_session)
            print(f"After: lesson1.google_event_id = {lesson1.google_event_id}")
            print(f"Expected: {event_id_1}")

            if lesson1.google_event_id == event_id_1:
                print("  [SUCCESS] Values match!")
            else:
                print("  [FAILURE] Values do not match!")

        except Exception as e:
            print(f"  [ERROR] {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    debug_cancellation_test()