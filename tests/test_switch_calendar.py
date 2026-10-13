#!/usr/bin/env python3
"""
Test for the switch_calendar_for_user method in GoogleCalendarSyncService.
"""
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database
from app.database.models import User, GoogleCalendarConnection, GoogleCalendarEvent, Lesson


def test_switch_calendar_for_user_success():
    """Test successful calendar switching."""
    print("Test: Successful calendar switching")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Mock connections
    source_connection = Mock()
    source_connection.id = 1
    source_connection.user_id = user_id
    source_connection.calendar_id = source_calendar_id
    source_connection.enabled = 1

    target_connection = Mock()
    target_connection.id = 2
    target_connection.user_id = user_id
    target_connection.calendar_id = target_calendar_id
    target_connection.enabled = 1

    # Mock lesson and event
    lesson = Mock()
    lesson.id = 101
    lesson.user_id = user_id
    lesson.google_event_id = "event_123"
    lesson.subject = "Test Lesson"
    lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    event_record = Mock()
    event_record.id = 201
    event_record.connection_id = source_connection.id
    event_record.google_event_id = lesson.google_event_id
    event_record.calendar_id = source_calendar_id
    event_record.summary = lesson.subject
    event_record.start_time = lesson.start_time
    event_record.end_time = lesson.end_time

    # Mock Google Calendar API responses
    source_event = {
        "id": "event_123",
        "summary": "Test Lesson",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed",
    }

    created_event = {
        "id": "new_event_456",
        "summary": "Test Lesson",
        "start": {"dateTime": "2026-10-08T19:00:00Z"},
        "end": {"dateTime": "2026-10-08T20:00:00Z"},
        "created": "2026-10-08T12:00:00Z",
        "updated": "2026-10-08T12:00:00Z",
        "status": "confirmed",
    }

    # Track session calls to return appropriate mocks
    session_call_count = 0

    def get_session_mock(*args, **kwargs):
        nonlocal session_call_count
        session_call_count += 1
        call_num = session_call_count
        print(f"[SESSION] Call #{call_num}")

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        if call_num == 1:
            # Session 1: GoogleCalendarSyncService.__init__ (getting user colors)
            print("  [SESSION 1] Returning User for color overrides")
            user_query_mock = Mock()
            user_filter_mock = Mock()
            user_filter_mock.first.return_value = Mock()  # Mock User
            user_query_mock.filter.return_value = user_filter_mock
            mock_session.query.return_value = user_query_mock
        elif call_num == 2:
            # Session 2: Outer session in switch_calendar_for_user (connections and lessons)
            print("  [SESSION 2] Setting up connections and lessons queries")
            query_counter = 0

            def query_side_effect(*args):
                nonlocal query_counter
                query_counter += 1
                print(f"    [SESSION 2] Query #{query_counter} with args: {args[0].__name__ if hasattr(args[0], '__name__') else str(args[0])}")

                if args[0] == GoogleCalendarConnection:
                    # Connection query (either source or target)
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    if query_counter == 1:
                        connection_filter_mock.first.return_value = source_connection
                    elif query_counter == 2:
                        connection_filter_mock.first.return_value = target_connection
                    else:
                        connection_filter_mock.first.return_value = None
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif args[0] == Lesson:
                    # Lessons query with join
                    print("    [SESSION 2] Building lessons query mock chain")
                    lesson_query_mock = Mock()

                    # Mock the join chain for: session.query(Lesson).join(...).filter(...).filter(...).all()
                    join_mock = Mock()
                    lesson_query_mock.join.return_value = join_mock
                    join_mock.filter.return_value = join_mock  # First filter
                    join_mock.filter.return_value = join_mock  # Second filter
                    join_mock.all.return_value = [lesson]   # Return actual list

                    return lesson_query_mock
                else:
                    # For any other query
                    return Mock()

            mock_session.query.side_effect = query_side_effect
        elif call_num >= 3:
            # Session 3+: Inner sessions for processing each lesson
            print(f"  [SESSION {call_num}] Setting up inner session for lesson processing")
            query_counter = 0

            def query_side_effect(*args):
                nonlocal query_counter
                query_counter += 1
                query_name = args[0].__name__ if hasattr(args[0], '__name__') else str(args[0])
                print(f"    [SESSION {call_num}] Query #{query_counter} ({query_name}) with args: {args}")

                if args[0] == Lesson:
                    # Query for lesson to process (with for_update)
                    if query_counter == 1:
                        lesson_query_mock = Mock()
                        filter_mock = Mock()
                        lesson_query_mock.filter.return_value = filter_mock
                        for_update_mock = Mock()
                        filter_mock.with_for_update.return_value = for_update_mock
                        for_update_mock.first.return_value = lesson  # Return our lesson
                        return lesson_query_mock
                elif args[0] == GoogleCalendarEvent:
                    # Query for event record (with for_update)
                    if query_counter == 1:  # This should be the first and only query in inner session
                        event_query_mock = Mock()
                        filter_mock = Mock()
                        event_query_mock.filter.return_value = filter_mock
                        for_update_mock = Mock()
                        filter_mock.with_for_update.return_value = for_update_mock
                        for_update_mock.first.return_value = event_record  # Return our event record
                        return event_query_mock
                else:
                    return Mock()

            mock_session.query.side_effect = query_side_effect
        else:
            # Fallback
            mock_session.query.return_value = Mock()

        return mock_session

    # Track service calls
    service_call_count = 0

    def get_service_mock(*args, **kwargs):
        nonlocal service_call_count
        service_call_count += 1
        call_num = service_call_count
        print(f"[SERVICE] Call #{call_num}")

        mock_service = Mock()
        if call_num == 1:
            # Source service
            print("  [SERVICE 1] Returning source service")
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(return_value=source_event)

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)
        else:
            # Target service
            print("  [SERVICE 2] Returning target service")
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(return_value=created_event)
        return mock_service

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = get_session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # Call the method
            print("[MAIN] Calling switch_calendar_for_user...")
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )

            print(f"\n[RESULT] Result: {result}")
            print(f"[INFO] Session calls made: {session_call_count}")
            print(f"[INFO] Service calls made: {service_call_count}")

            # Assertions
            assert result == 1, f"Expected 1 processed lesson, got {result}"
            # Check that the lesson's google_event_id was updated
            assert lesson.google_event_id == "new_event_456"
            # Check that the event record was updated
            assert event_record.connection_id == target_connection.id
            assert event_record.google_event_id == "new_event_456"
            assert event_record.calendar_id == target_calendar_id

            print("  [OK] switch_calendar_for_user processed lesson successfully")


def test_switch_calendar_for_user_missing_connections():
    """Test switching when one of the connections is missing."""
    print("\nTest: Missing connections")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Mock only source connection (target missing)
    source_connection = Mock()
    source_connection.id = 1
    source_connection.user_id = user_id
    source_connection.calendar_id = source_calendar_id
    source_connection.enabled = 1

    # Track session calls
    session_call_count = 0

    def get_session_mock(*args, **kwargs):
        nonlocal session_call_count
        session_call_count += 1
        call_num = session_call_count

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        if call_num == 1:
            # Session 1: GoogleCalendarSyncService.__init__ (getting user colors)
            user_query_mock = Mock()
            user_filter_mock = Mock()
            user_filter_mock.first.return_value = Mock()  # Mock User
            user_query_mock.filter.return_value = user_filter_mock
            mock_session.query.return_value = user_query_mock
        elif call_num == 2:
            # Session 2: Outer session in switch_calendar_for_user
            query_counter = 0

            def query_side_effect(*args):
                nonlocal query_counter
                query_counter += 1

                if args[0] == GoogleCalendarConnection:
                    # Connection query
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    if query_counter == 1:
                        connection_filter_mock.first.return_value = source_connection
                    elif query_counter == 2:
                        connection_filter_mock.first.return_value = None  # Target connection missing
                    else:
                        connection_filter_mock.first.return_value = None
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif args[0] == Lesson:
                    # Lessons query - won't matter since target connection is missing
                    lesson_query_mock = Mock()
                    join_mock = Mock()
                    lesson_query_mock.join.return_value = join_mock
                    join_mock.filter.return_value = join_mock
                    join_mock.filter.return_value = join_mock
                    join_mock.all.return_value = []  # No lessons
                    return lesson_query_mock
                else:
                    return Mock()

            mock_session.query.side_effect = query_side_effect
        else:
            # Fallback for any other sessions
            mock_session.query.return_value = Mock()

        return mock_session

    # No service calls should happen since we return early due to missing connection
    service_call_count = 0

    def get_service_mock(*args, **kwargs):
        nonlocal service_call_count
        service_call_count += 1
        return Mock()

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = get_session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # Call the method
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )

            # Assertions
            assert result == 0, f"Expected 0 processed lessons due to missing connection, got {result}"
            assert service_call_count == 0, f"Expected 0 service calls, got {service_call_count}"

            print("  [OK] switch_calendar_for_user returned 0 when target connection missing")


def test_switch_calendar_for_user_no_lessons():
    """Test switching when there are no lessons to switch."""
    print("\nTest: No lessons to switch")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Mock connections
    source_connection = Mock()
    source_connection.id = 1
    source_connection.user_id = user_id
    source_connection.calendar_id = source_calendar_id
    source_connection.enabled = 1

    target_connection = Mock()
    target_connection.id = 2
    target_connection.user_id = user_id
    target_connection.calendar_id = target_calendar_id
    target_connection.enabled = 1

    # Track session calls
    session_call_count = 0

    def get_session_mock(*args, **kwargs):
        nonlocal session_call_count
        session_call_count += 1
        call_num = session_call_count

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        if call_num == 1:
            # Session 1: GoogleCalendarSyncService.__init__ (getting user colors)
            user_query_mock = Mock()
            user_filter_mock = Mock()
            user_filter_mock.first.return_value = Mock()  # Mock User
            user_query_mock.filter.return_value = user_filter_mock
            mock_session.query.return_value = user_query_mock
        elif call_num == 2:
            # Session 2: Outer session in switch_calendar_for_user (connections and lessons)
            query_counter = 0

            def query_side_effect(*args):
                nonlocal query_counter
                query_counter += 1

                if args[0] == GoogleCalendarConnection:
                    # Connection query
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    if query_counter == 1:
                        connection_filter_mock.first.return_value = source_connection
                    elif query_counter == 2:
                        connection_filter_mock.first.return_value = target_connection
                    else:
                        connection_filter_mock.first.return_value = None
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif args[0] == Lesson:
                    # Lessons query - return empty list
                    lesson_query_mock = Mock()
                    join_mock = Mock()
                    lesson_query_mock.join.return_value = join_mock
                    join_mock.filter.return_value = join_mock
                    join_mock.filter.return_value = join_mock
                    join_mock.all.return_value = []  # No lessons
                    return lesson_query_mock
                else:
                    return Mock()

            mock_session.query.side_effect = query_side_effect
        else:
            # Fallback for any other sessions
            mock_session.query.return_value = Mock()

        return mock_session

    # Track service calls - should not be called since no lessons to process
    service_call_count = 0

    def get_service_mock(*args, **kwargs):
        nonlocal service_call_count
        service_call_count += 1
        return Mock()

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = get_session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # Call the method
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )

            # Assertions
            assert result == 0, f"Expected 0 processed lessons when no lessons, got {result}"
            assert service_call_count == 0, f"Expected 0 service calls, got {service_call_count}"

            print("  [OK] switch_calendar_for_user returned 0 when no lessons to switch")


if __name__ == "__main__":
    print("Testing switch_calendar_for_user...")
    print("=" * 50)

    try:
        test_switch_calendar_for_user_success()
        test_switch_calendar_for_user_missing_connections()
        test_switch_calendar_for_user_no_lessons()

        print("=" * 50)
        print("All tests passed! [OK]")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)