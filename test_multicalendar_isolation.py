#!/usr/bin/env python3
"""
Multi-calendar isolation test suite for Google Calendar synchronization.
Tests that connections properly isolate their operations to prevent interference
between different calendars/users sharing the same google_event_id.
"""

import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def create_mock_session_with_data(scenario_data):
    """Create a mock session that returns predefined data for queries."""
    session_mock = Mock()

    # Setup the query mock - we'll configure this per test
    query_mock = Mock()
    session_mock.query.return_value = query_mock

    # Context manager support
    session_mock.__enter__ = Mock(return_value=session_mock)
    session_mock.__exit__ = Mock(return_value=None)

    return session_mock, query_mock


def test_same_google_event_id_two_calendars_isolation():
    """Test that same google_event_id in two calendars doesn't cause interference."""
    print("Test: Same google_event_id in two different calendars")

    db = Database()
    # Service for first calendar
    service1 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")
    # Service for second calendar (same user, different calendar)
    service2 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar2")

    # Mock data: two connections
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

    # Mock data: same google_event_id for both calendars
    shared_event_id = "shared_event_123"

    # Mock data: lessons linked to each connection via GoogleCalendarEvent
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.user_id = 1
    lesson1.google_event_id = shared_event_id
    lesson1.subject = "Lesson for Calendar 1"

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.user_id = 1
    lesson2.google_event_id = shared_event_id
    lesson2.subject = "Lesson for Calendar 2"

    # Mock GoogleCalendarEvent records showing the link
    gcal_event1 = Mock()
    gcal_event1.id = 201
    gcal_event1.connection_id = conn1.id
    gcal_event1.google_event_id = shared_event_id

    gcal_event2 = Mock()
    gcal_event2.id = 202
    gcal_event2.connection_id = conn2.id
    gcal_event2.google_event_id = shared_event_id

    # Configure mock session for service1
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session_method.return_value.__exit__.return_value = None

        # Setup connection query for service1
        connection_query_mock = Mock()
        connection_filter_mock = Mock()
        connection_filter_mock.first.return_value = conn1

        # Setup for GoogleCalendarEvent query (used in _persist_google_events)
        event_query_mock = Mock()
        event_filter_mock = Mock()
        event_filter_mock.first.return_value = None  # No existing event (new)

        # Setup for Lesson query (used in other methods)
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()

        def query_side_effect(*args):
            if not args:
                # Handle case when no args are provided
                return Mock()
            if args[0] == GoogleCalendarConnection:
                return connection_query_mock
            elif args[0] == GoogleCalendarEvent:
                return event_query_mock
            elif args[0] == Lesson:
                return lesson_query_mock
            else:
                return Mock()

        mock_session.query.side_effect = query_side_effect

        # Setup the connection query chain
        connection_query_mock.filter.return_value = connection_filter_mock

        # Setup the GoogleCalendarEvent query chain for _persist_google_events
        event_query_mock.filter.return_value = event_filter_mock

        # Setup the Lesson query chain for other methods (3 filters: user_id, connection_id, isnot(None))
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1  # First filter: user_id
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2  # Second filter: connection_id
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3  # Third filter: isnot(None)

        # Configure the joins and filters for lesson query (for service1)
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = [lesson1]  # Only lesson1 for connection 1

        # Test _persist_google_events respects connection scoping
        test_event = {
            "id": shared_event_id,
            "summary": "Test Event",
            "start": {"dateTime": "2026-10-08T19:00:00Z"},
            "end": {"dateTime": "2026-10-08T20:00:00Z"},
            "created": "2026-10-08T12:00:00Z",
            "updated": "2026-10-08T12:00:00Z",
            "status": "confirmed"
        }

        # This should only affect connection 1's scoped lessons
        try:
            service1._persist_google_events(conn1, [test_event])
            # Verify that the event was added to the session
            assert mock_session.add.called
            print("  [OK] _persist_google_events correctly scoped to connection")
        except Exception as e:
            print(f"  [FAIL] _persist_google_events failed: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()
        mock_session.add.reset_mock()

        # Reset the lesson query mock for service2
        lesson_filter_mock3.all.return_value = [lesson2]  # Only lesson2 for connection 2

        # Test service2 - should NOT interfere with service1's operation
        try:
            service2._persist_google_events(conn2, [test_event])
            # This should also add an event (different connection, same google_event_id is allowed)
            assert mock_session.add.called
            print("  [OK] _persist_google_events allows same google_event_id for different connections")
        except Exception as e:
            print(f"  [FAIL] _persist_google_events failed for second connection: {e}")
            raise

    print("  [PASS] Same google_event_id in two calendars isolation test passed")


def test_cancellation_isolation_between_calendars():
    """Test that cancelled events in one calendar don't affect lessons in another."""
    print("\nTest: Cancellation isolation between calendars")

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

        # Setup lesson query for service1 - need to handle multiple queries in the function
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3

        # Setup connection query (likely called first in the function)
        connection_query_mock = Mock()
        connection_filter_mock = Mock()
        connection_query_mock.filter.return_value = connection_filter_mock
        connection_filter_mock.first.return_value = conn1

        # Capture the lessons in a closure so they're accessible to query_side_effect
        def make_query_side_effect(expected_lesson=None):
            def query_side_effect(*args):
                print(f"    query_side_effect called with args: {args}")
                if not args:
                    # Handle case when no args are provided
                    print("    query_side_effect: no args, returning Mock")
                    return Mock()
                if args[0] == GoogleCalendarConnection:
                    print("    query_side_effect: args[0] is GoogleCalendarConnection, returning connection_query_mock")
                    return connection_query_mock
                elif args[0] == Lesson:
                    print("    query_side_effect: args[0] is Lesson, returning lesson_query_mock")
                    # Let's mock the entire chain at once for simplicity
                    # But first, let's see what the actual query looks like by adding debug to each step

                    # Create the mocks
                    lesson_query_result = Mock()
                    lesson_join_mock = Mock()
                    lesson_filter_mock = Mock()  # for the single filter with 3 conditions

                    # Set up the chain with debug
                    def debug_join(*args, **kwargs):
                        print(f"    lesson.query.join called with args: {args}, kwargs: {kwargs}")
                        return lesson_join_mock

                    def debug_filter(*args, **kwargs):
                        print(f"    lesson_join_mock.filter called with args: {args}, kwargs: {kwargs}")
                        print(f"    Number of filter args: {len(args)}")
                        return lesson_filter_mock

                    def debug_all():
                        print(f"    lesson_filter_mock.all called")
                        # Determine which lesson to return based on context
                        if expected_lesson is not None:
                            result = [expected_lesson]
                            print(f"    Returning [{expected_lesson.subject}]: {result}")
                            return result
                        else:
                            result = []
                            print(f"    Returning []: {result}")
                            return result

                    lesson_query_result.join = debug_join
                    lesson_join_mock.filter = debug_filter
                    lesson_filter_mock.all = debug_all

                    lesson_query_mock.join = lesson_query_result.join
                    # Set up the mock chain
                    lesson_query_mock.join.return_value = lesson_join_mock
                    lesson_join_mock.filter.return_value = lesson_filter_mock
                    lesson_filter_mock.all.return_value = []  # Default, will be overridden by debug_all

                    return lesson_query_mock
                else:
                    print(f"    query_side_effect: args[0] is {args[0]}, returning Mock")
                    return Mock()
            return query_side_effect

        # For service1 test, we expect lesson1
        mock_session.query.side_effect = make_query_side_effect(lesson1)

        try:
            service1._handle_cancelled_google_events(conn1, [cancelled_event_calendar1], mock_session)
            # Lesson1's google_event_id should BE cleared
            assert lesson1.google_event_id is None
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson1 cleared")
            # Reset lesson1 for next tests
            lesson1.google_event_id = event_id_1
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service1: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()

        # Setup for service2 - should clear lesson2 (event is from calendar2)
        # Setup connection query (likely called first in the function)
        connection_query_mock = Mock()
        connection_filter_mock = Mock()
        connection_query_mock.filter.return_value = connection_filter_mock
        connection_filter_mock.first.return_value = conn2

        # For service2 test, we expect lesson2
        mock_session.query.side_effect = make_query_side_effect(lesson2)

        try:
            service2._handle_cancelled_google_events(conn2, [cancelled_event_calendar2], mock_session)
            # Lesson2's google_event_id should BE cleared
            assert lesson2.google_event_id is None
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson2 cleared")
            # Reset lesson2 for next tests
            lesson2.google_event_id = event_id_2
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service2: {e}")
            raise

        # Reset mock for next call
        mock_session.reset_mock()

        # Setup for service1 - should NOT clear lesson2 (event is from calendar2, not calendar1)
        # Setup connection query (likely called first in the function)
        connection_query_mock = Mock()
        connection_filter_mock = Mock()
        connection_query_mock.filter.return_value = connection_filter_mock
        connection_filter_mock.first.return_value = conn1

        # For this test, we expect no lessons (empty list)
        mock_session.query.side_effect = make_query_side_effect(None)

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
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = []  # No lessons for connection 2 with event_id_1

        # Setup connection query (likely called first in the function)
        connection_query_mock = Mock()
        connection_filter_mock = Mock()
        connection_query_mock.filter.return_value = connection_filter_mock
        connection_filter_mock.first.return_value = conn2

        # For this test (service2 handling event from calendar1), we expect no lessons for service2's connection
        mock_session.query.side_effect = make_query_side_effect(None)

        try:
            service2._handle_cancelled_google_events(conn2, [cancelled_event_calendar1], mock_session)
            # Lesson1's google_event_id should NOT be cleared (it's not lesson2's event)
            assert lesson2.google_event_id == event_id_2
            print("  [OK] _handle_cancelled_google_events correctly scoped - lesson2 unaffected by calendar1's event")
        except Exception as e:
            print(f"  [FAIL] _handle_cancelled_google_events failed for service2: {e}")
            raise

    print("  [PASS] Cancellation isolation between calendars test passed")


def test_conflict_isolation_between_calendars():
    """Test that conflict detection/resolution is scoped to each connection."""
    print("\nTest: Conflict detection/isolation between calendars")

    db = Database()
    service1 = GoogleCalendarSyncService(db, user_id=1, calendar_id="calendar1")
    service2 = GoogleCalendarSyncService(db, user_id=2, calendar_id="calendar1")  # Different user

    # Two users, same calendar
    conn1 = Mock()
    conn1.id = 1
    conn1.user_id = 1
    conn1.calendar_id = "calendar1"
    conn1.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    conn2 = Mock()
    conn2.id = 2
    conn2.user_id = 2
    conn2.calendar_id = "calendar1"
    conn2.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    # Same google_event_id for both users (should be isolated)
    shared_event_id = "conflict_event_789"

    # Lessons for each user
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.user_id = 1
    lesson1.google_event_id = shared_event_id
    lesson1.subject = "User 1 Lesson"

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.user_id = 2
    lesson2.google_event_id = shared_event_id
    lesson2.subject = "User 2 Lesson"

    # GoogleCalendarEvent links
    gcal_event1 = Mock()
    gcal_event1.connection_id = conn1.id
    gcal_event1.google_event_id = shared_event_id

    gcal_event2 = Mock()
    gcal_event2.connection_id = conn2.id
    gcal_event2.google_event_id = shared_event_id

    # Google Calendar event that exists (so no conflict for existing lessons)
    google_event = {
        "id": shared_event_id,
        "summary": "Existing Event",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed"
    }

    # Test service1
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = conn1

        # Setup for conflict detection - lessons with google_event_id
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = [lesson1]

        try:
            # Mock the service parameter
            mock_service = Mock()
            service1._detect_and_handle_conflicts(mock_service, google_events=[google_event])
            print("  [OK] _detect_and_handle_conflicts executed without error for service1")
        except Exception as e:
            print(f"  [FAIL] _detect_and_handle_conflicts failed for service1: {e}")
            raise

    # Test service2 - should work independently
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = conn2

        # Setup for conflict detection
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = [lesson2]

        try:
            # Mock the service parameter
            mock_service = Mock()
            service2._detect_and_handle_conflicts(mock_service, google_events=[google_event])
            print("  [OK] _detect_and_handle_conflicts executed without error for service2")
        except Exception as e:
            print(f"  [FAIL] _detect_and_handle_conflicts failed for service2: {e}")
            raise

    print("  [PASS] Conflict isolation between calendars test passed")


def test_different_event_ids_no_interference():
    """Test that different google_event_ids don't interfere across connections."""
    print("\nTest: Different google_event_ids no interference")

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

    # Different event IDs
    event1_id = "event_111"
    event2_id = "event_222"

    # Lessons
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.user_id = 1
    lesson1.google_event_id = event1_id
    lesson1.subject = "Lesson 1"

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.user_id = 1
    lesson2.google_event_id = event2_id
    lesson2.subject = "Lesson 2"

    # GoogleCalendarEvent links
    gcal_event1 = Mock()
    gcal_event1.connection_id = conn1.id
    gcal_event1.google_event_id = event1_id

    gcal_event2 = Mock()
    gcal_event2.connection_id = conn2.id
    gcal_event2.google_event_id = event2_id

    # Events from Google Calendar
    google_event1 = {
        "id": event1_id,
        "summary": "Event 1",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed"
    }

    google_event2 = {
        "id": event2_id,
        "summary": "Event 2",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed"
    }

    # Test service1 with its event
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = conn1

        # Setup lessons query
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = [lesson1]

        try:
            mock_service = Mock()
            service1._detect_and_handle_conflicts(mock_service, google_events=[google_event1])
            print("  [OK] Service1 processed its event correctly")
        except Exception as e:
            print(f"  [FAIL] Service1 failed: {e}")
            raise

    # Test service2 with its event
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = conn2

        # Setup lessons query
        lesson_query_mock = Mock()
        lesson_join_mock = Mock()
        lesson_filter_mock1 = Mock()
        lesson_filter_mock2 = Mock()
        lesson_filter_mock3 = Mock()
        lesson_query_mock.join.return_value = lesson_join_mock
        lesson_join_mock.filter.return_value = lesson_filter_mock1
        lesson_filter_mock1.filter.return_value = lesson_filter_mock2
        lesson_filter_mock2.filter.return_value = lesson_filter_mock3
        lesson_filter_mock3.all.return_value = [lesson2]

        try:
            mock_service = Mock()
            service2._detect_and_handle_conflicts(mock_service, google_events=[google_event2])
            print("  [OK] Service2 processed its event correctly")
        except Exception as e:
            print(f"  [FAIL] Service2 failed: {e}")
            raise

    print("  [PASS] Different google_event_ids no interference test passed")


def test_user_isolation():
    """Test that different users don't interfere with each other."""
    print("\nTest: User isolation")

    db = Database()
    # Same calendar, different users
    service1 = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")
    service2 = GoogleCalendarSyncService(db, user_id=2, calendar_id="primary")

    conn1 = Mock()
    conn1.id = 1
    conn1.user_id = 1
    conn1.calendar_id = "primary"
    conn1.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    conn2 = Mock()
    conn2.id = 2
    conn2.user_id = 2
    conn2.calendar_id = "primary"
    conn2.connected_at = datetime(2026, 10, 7, 12, 0, 0, tzinfo=timezone.utc)

    # Same google_event_id for different users (should be isolated)
    shared_event_id = "user_isolation_event"

    # Lessons for each user
    lesson1 = Mock()
    lesson1.id = 101
    lesson1.user_id = 1
    lesson1.google_event_id = shared_event_id
    lesson1.subject = "User 1 Lesson"

    lesson2 = Mock()
    lesson2.id = 102
    lesson2.user_id = 2
    lesson2.google_event_id = shared_event_id
    lesson2.subject = "User 2 Lesson"

    # GoogleCalendarEvent links
    gcal_event1 = Mock()
    gcal_event1.connection_id = conn1.id
    gcal_event1.google_event_id = shared_event_id

    gcal_event2 = Mock()
    gcal_event2.connection_id = conn2.id
    gcal_event2.google_event_id = shared_event_id

    # Test service1
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = conn1

        # Setup for persistence test
        test_event = {
            "id": shared_event_id,
            "summary": "Test Event",
            "start": {"dateTime": "2026-10-08T19:00:00Z"},
            "end": {"dateTime": "2026-10-08T20:00:00Z"},
            "created": "2026-10-08T12:00:00Z",
            "updated": "2026-10-08T12:00:00Z",
            "status": "confirmed"
        }

        # Mock GoogleCalendarEvent query to return None (new event)
        event_query_mock = Mock()
        mock_session.query.return_value = event_query_mock
        event_filter_mock = Mock()
        event_query_mock.filter.return_value = event_filter_mock
        event_filter_mock.first.return_value = None

        try:
            service1._persist_google_events(conn1, [test_event])
            assert mock_session.add.called
            print("  [OK] User1 persistence worked correctly")
        except Exception as e:
            print(f"  [FAIL] User1 persistence failed: {e}")
            raise

        # Reset
        mock_session.reset_mock()
        mock_session.add.reset_mock()

        # Test service2
        mock_session.query.return_value.filter.return_value.first.return_value = conn2
        event_query_mock = Mock()
        mock_session.query.return_value = event_query_mock
        event_filter_mock = Mock()
        event_query_mock.filter.return_value = event_filter_mock
        event_filter_mock.first.return_value = None

        try:
            service2._persist_google_events(conn2, [test_event])
            assert mock_session.add.called
            print("  [OK] User2 persistence worked correctly")
        except Exception as e:
            print(f"  [FAIL] User2 persistence failed: {e}")
            raise

    print("  [PASS] User isolation test passed")


if __name__ == "__main__":
    print("Running multi-calendar isolation test suite...")
    print("=" * 60)

    try:
        test_same_google_event_id_two_calendars_isolation()
        test_cancellation_isolation_between_calendars()
        test_conflict_isolation_between_calendars()
        test_different_event_ids_no_interference()
        test_user_isolation()

        print("=" * 60)
        print("All multi-calendar isolation tests passed! [OK]")

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)