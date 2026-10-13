#!/usr/bin/env python3
"""
Final test for the switch_calendar_for_user method in GoogleCalendarSyncService.
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
    """Test successful calendar switching with proper object sharing."""
    print("Test: Successful calendar switching")

    db = Database()
    user_id = 1
    source_calendar_id = "source_calendar_id"
    target_calendar_id = "target_calendar_id"

    # Create the actual lesson and event objects we'll share throughout
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"
    test_lesson.subject = "Test Lesson"
    test_lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    test_lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    test_event_record = GoogleCalendarEvent()
    test_event_record.id = 201
    test_event_record.connection_id = 1  # Will be set properly later
    test_event_record.google_event_id = test_lesson.google_event_id  # Share same ID initially
    test_event_record.calendar_id = source_calendar_id
    test_event_record.summary = test_lesson.subject
    test_event_record.start_time = test_lesson.start_time
    test_event_record.end_time = test_lesson.end_time

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

    # Track session calls
    session_calls = []

    def session_mock(*args, **kwargs):
        session_calls.append(len(session_calls) + 1)
        call_num = len(session_calls)

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        # Track query number within this session
        query_num = 0

        def query_side_effect(*args):
            nonlocal query_num
            query_num += 1

            if call_num == 1:
                # This is the session from GoogleCalendarSyncService.__init__ (for user colors)
                if query_num == 1:
                    # Query for User to get color overrides
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    user_filter_mock.first.return_value = Mock()  # Return a mock User
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                else:
                    return Mock()
            elif call_num == 2:
                # This is the outer session in switch_calendar_for_user (for connections and lessons)
                if query_num == 1:
                    # First query: source_connection
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    connection_filter_mock.first.return_value = source_connection
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif query_num == 2:
                    # Second query: target_connection
                    connection_query_mock = Mock()
                    connection_filter_mock = Mock()
                    connection_filter_mock.first.return_value = target_connection
                    connection_query_mock.filter.return_value = connection_filter_mock
                    return connection_query_mock
                elif query_num >= 3:
                    # Third query+: lessons (the complex join query)
                    # Build the mock chain properly: each method returns self for chaining, except .all()

                    # Start with the query mock for Lesson
                    lesson_query_mock = Mock()

                    # Mock .join(GoogleCalendarEvent, Lesson.google_event_id == GoogleCalendarEvent.google_event_id)
                    # For chaining, .join() should return the query object itself
                    lesson_query_mock.join.return_value = lesson_query_mock

                    # Mock first .filter(Lesson.user_id == user_id)
                    # For chaining, .filter() should return the query object itself
                    lesson_query_mock.filter.return_value = lesson_query_mock

                    # Mock second .filter(GoogleCalendarEvent.connection_id == source_connection.id)
                    # For chaining, .filter() should return the query object itself
                    lesson_query_mock.filter.return_value = lesson_query_mock

                    # Mock .all() to return our lessons list (this should return the actual list containing our lesson instance)
                    result_list = [test_lesson]  # Return a REAL list containing our test_lesson instance
                    lesson_query_mock.all.return_value = result_list

                    return lesson_query_mock
                else:
                    return Mock()
            else:
                # These are inner sessions (for processing each lesson)
                if query_num == 1:
                    # First query: get lesson to process (with for_update)
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = test_lesson  # RETURN THE SAME LESSON INSTANCE
                    return lesson_query_mock
                elif query_num == 2:
                    # Second query: get event record (with for_update)
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock
                    # Simulate .with_for_update().first()
                    for_update_mock = Mock()
                    filter_mock.with_for_update.return_value = for_update_mock
                    for_update_mock.first.return_value = test_event_record  # RETURN THE SAME EVENT INSTANCE
                    return event_query_mock
                else:
                    return Mock()

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Mock the get_google_calendar_service function
    service_calls = []
    def get_service_mock(*args, **kwargs):
        service_calls.append(len(service_calls) + 1)

        mock_service = Mock()
        if len(service_calls) == 0:  # First call
            # Source service
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(return_value=source_event)

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)
        else:  # Second call
            # Target service
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(return_value=created_event)
        return mock_service

    with patch.object(db, 'session') as mock_session_method:
        mock_session_method.side_effect = session_mock

        with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # Call the method
            result = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, source_calendar_id, target_calendar_id
            )

            # Assertions
            assert result == 1, f"Expected 1 processed lesson, got {result}"
            # Check that the lesson's google_event_id was updated (same object reference)
            assert test_lesson.google_event_id == "new_event_456"
            # Check that the event record was updated
            assert test_event_record.connection_id == target_connection.id
            assert test_event_record.google_event_id == "new_event_456"
            assert test_event_record.calendar_id == target_calendar_id


def test_switch_calendar_for_user_missing_connections():
    """Test switching when one of the connections is missing."""
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

    def get_session_mock(*args, **kwargs):
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        # Simple mock that handles the expected queries
        def query_side_effect(*args):
            if args[0] == GoogleCalendarConnection:
                connection_query_mock = Mock()
                connection_filter_mock = Mock()
                # First call: source, Second call: target (which returns None)
                if not hasattr(query_side_effect, "call_count"):
                    query_side_effect.call_count = 0
                query_side_effect.call_count += 1
                if query_side_effect.call_count == 1:
                    connection_filter_mock.first.return_value = source_connection
                else:
                    connection_filter_mock.first.return_value = None  # Target missing
                connection_query_mock.filter.return_value = connection_filter_mock
                return connection_query_mock
            elif args[0] == Lesson:
                # Return empty lessons list
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
        return mock_session

    # No service calls should happen
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


def test_switch_calendar_for_user_no_lessons():
    """Test switching when there are no lessons to switch."""
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

    def get_session_mock(*args, **kwargs):
        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        # Simple mock that handles the expected queries
        def query_side_effect(*args):
            if args[0] == GoogleCalendarConnection:
                connection_query_mock = Mock()
                connection_filter_mock = Mock()
                # First call: source, Second call: target
                if not hasattr(query_side_effect, "call_count"):
                    query_side_effect.call_count = 0
                query_side_effect.call_count += 1
                if query_side_effect.call_count == 1:
                    connection_filter_mock.first.return_value = source_connection
                else:
                    connection_filter_mock.first.return_value = target_connection
                connection_query_mock.filter.return_value = connection_filter_mock
                return connection_query_mock
            elif args[0] == Lesson:
                # Return empty lessons list
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


if __name__ == "__main__":
    # Run the tests
    test_switch_calendar_for_user_success()
    test_switch_calendar_for_user_missing_connections()
    test_switch_calendar_for_user_no_lessons()
    print("All tests passed!")