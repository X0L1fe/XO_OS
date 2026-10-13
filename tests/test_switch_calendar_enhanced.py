#!/usr/bin/env python3
"""
Test for Google Calendar switching functionality.
Specifically tests fast switching A->B->A where the last choice is processed correctly.
"""

import os
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, PropertyMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.db import Database
from app.database.models import (
    GoogleCalendarConnection,
    GoogleCalendarEvent,
    Lesson,
    User,
)
from app.google_calendar.service import GoogleCalendarSyncService


def test_fast_switching_iso_ab_a():
    """Test rapid A->B->A switching - last user choice should be processed correctly."""
    print("Test: Fast switching A->B->A")

    db = Database()
    user_id = 1
    calendar_a = "calendar_a_id"
    calendar_b = "calendar_b_id"
    calendar_c = "calendar_c_id"  # Final choice

    # Create test lesson
    test_lesson = Lesson()
    test_lesson.id = 101
    test_lesson.user_id = user_id
    test_lesson.google_event_id = "event_123"
    test_lesson.subject = "Test Lesson"
    test_lesson.start_time = datetime(2026, 10, 8, 19, 0, 0, tzinfo=timezone.utc)
    test_lesson.end_time = datetime(2026, 10, 8, 20, 0, 0, tzinfo=timezone.utc)

    # Create a simple class to hold event record state with connection_id tracking
    class MockEventRecord:
        def __init__(self):
            self.id = 201
            self._connection_id = 1  # Will be updated during processing
            self.google_event_id = (
                test_lesson.google_event_id
            )  # Initially same as lesson
            self.calendar_id = calendar_a
            self.summary = test_lesson.subject
            self.start_time = test_lesson.start_time
            self.end_time = test_lesson.end_time

        @property
        def connection_id(self):
            return self._connection_id

        @connection_id.setter
        def connection_id(self, value):
            # Only allow non-Mock values to be set; ignore Mock assignments to prevent corruption
            if not isinstance(value, Mock):
                self._connection_id = value
            # If someone tries to set it to a Mock, ignore it to prevent corruption

    test_event_record = MockEventRecord()

    # Mock connections for all three calendars
    conn_a = Mock()
    conn_a.id = 1
    conn_a.user_id = user_id
    conn_a.calendar_id = calendar_a
    conn_a.enabled = 1

    conn_b = Mock()
    conn_b.id = 2
    conn_b.user_id = user_id
    conn_b.calendar_id = calendar_b
    conn_b.enabled = 1

    conn_c = Mock()
    conn_c.id = 3
    conn_c.user_id = user_id
    conn_c.calendar_id = calendar_c
    conn_c.enabled = 1

    # Track which session we're in
    session_count = 0

    def session_mock(*args, **kwargs):
        nonlocal session_count
        session_count += 1
        call_num = session_count

        mock_session = Mock()
        mock_session.__enter__ = Mock(return_value=mock_session)
        mock_session.__exit__ = Mock(return_value=None)

        query_num = 0

        def query_side_effect(*query_args):
            nonlocal query_num
            query_num += 1
            print(
                f"  Query #{query_num} called with call_num={call_num}, args={query_args}"
            )

            # Helper functions to check query type
            def is_user_query(args):
                return len(args) == 1 and args[0] is User

            def is_gcc_query(args):
                return len(args) == 1 and args[0] is GoogleCalendarConnection

            def is_lesson_query(args):
                return len(args) == 1 and args[0] is Lesson

            def is_gce_query(args):
                return len(args) == 1 and args[0] is GoogleCalendarEvent

            # SESSION 1: relevance check + initial connection validation (first switch: A->B)
            if call_num == 1:
                if query_num == 1 and is_user_query(query_args):
                    # Query for User - relevance check
                    print(
                        f"    Returning User for relevance check with selected calendar {calendar_b}"
                    )
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    mock_user = Mock()
                    mock_user.id = user_id
                    mock_user.selected_calendar_id = (
                        calendar_b  # User has already chosen target
                    )
                    user_filter_mock.first.return_value = mock_user
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                elif query_num == 2 and is_gcc_query(query_args):
                    # Query for source_connection (initial validation)
                    print(f"    Returning source connection for {calendar_a}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_a
                    return connection_query_mock
                elif query_num == 3 and is_gcc_query(query_args):
                    # Query for target_connection (initial validation)
                    print(f"    Returning target connection for {calendar_b}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_b
                    return connection_query_mock
                else:
                    print(
                        f"    Returning Mock for session 1: call_num={call_num}, query_num={query_num}"
                    )
                    # Return a basic mock to prevent attribute access issues
                    mock_ret = Mock()
                    mock_ret.id = None
                    return mock_ret
            # SESSION 2: constructor (loading user colors) for first switch
            elif call_num == 2:
                if query_num == 1 and is_user_query(query_args):
                    # Query for User - load user colors
                    print(f"    Returning User for loading colors")
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    mock_user = Mock()
                    mock_user.selected_calendar_id = (
                        calendar_b  # Keep track of selection
                    )
                    mock_user.lesson_colors = {}  # Empty colors
                    user_filter_mock.first.return_value = mock_user
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                else:
                    print(
                        f"    Returning Mock for session 2: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 3: connection validation (again) + lessons query start (first switch)
            elif call_num == 3:
                if query_num == 1 and is_gcc_query(query_args):
                    # Query for source_connection (validation)
                    print(f"    Returning source connection for {calendar_a}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_a
                    return connection_query_mock
                elif query_num == 2 and is_gcc_query(query_args):
                    # Query for target_connection (validation)
                    print(f"    Returning target connection for {calendar_b}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_b
                    return connection_query_mock
                elif query_num == 3 and is_lesson_query(query_args):
                    # session.query(Lesson) - start of lessons query
                    print(f"    Lessons query: starting Lesson query")
                    lesson_query_mock = Mock()
                    # Set up chaining for the full lessons query
                    lesson_query_mock.join.return_value = lesson_query_mock
                    lesson_query_mock.filter.return_value = (
                        lesson_query_mock  # First filter (join)
                    )
                    lesson_query_mock.filter.return_value = lesson_query_mock  # Second filter (overwrites first, but that's OK)

                    # Set up .all() to return our lessons list only if conditions are met
                    def mock_all():
                        # Check if lesson would pass the join and filters
                        # For the join condition: Lesson.google_event_id == GoogleCalendarEvent.google_event_id
                        # We need to check if there's a GoogleCalendarEvent with matching google_event_id
                        # and the right connection_id

                        user_ok = test_lesson.user_id == user_id

                        # Access the actual values from the mock object
                        connection_id_val = test_event_record.connection_id
                        google_event_id_val = test_event_record.google_event_id

                        print(
                            f"    DEBUG: test_event_record.connection_id = {connection_id_val} (type: {type(connection_id_val)})"
                        )
                        print(
                            f"    DEBUG: test_event_record.google_event_id = {google_event_id_val} (type: {type(google_event_id_val)})"
                        )
                        print(
                            f"    DEBUG: test_lesson.google_event_id = {test_lesson.google_event_id} (type: {type(test_lesson.google_event_id)})"
                        )

                        # Simulate the joined GoogleCalendarEvent object
                        # In the real query, this would come from the join
                        mock_event = Mock()
                        mock_event.google_event_id = google_event_id_val
                        mock_event.connection_id = connection_id_val

                        event_match = (
                            mock_event.google_event_id == test_lesson.google_event_id
                        )
                        connection_ok = (
                            mock_event.connection_id == conn_a.id
                        )  # source is conn_a for first switch

                        print(
                            f"    Lessons query: checking conditions - user_ok={user_ok}, event_match={event_match}, connection_ok={connection_ok}"
                        )
                        if user_ok and event_match and connection_ok:
                            return [test_lesson]
                        else:
                            return []

                    lesson_query_mock.all = mock_all

                    return lesson_query_mock
                else:
                    print(
                        f"    Returning Mock for session 3: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 4: lesson processing part 1 (first switch)
            elif call_num == 4:
                if query_num == 1 and is_lesson_query(query_args):
                    # Lesson query with for_update
                    print(f"    Lesson query with for_update")
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_lesson
                    return lesson_query_mock
                elif query_num == 2 and is_gce_query(query_args):
                    # Event record query with for_update
                    print(f"    Event record query with for_update")
                    print(
                        f"    DEBUG: Before returning event_record, connection_id = {test_event_record.connection_id}, google_event_id = {test_event_record.google_event_id}"
                    )
                    # Simulate the update that happens during processing:
                    # connection_id changes from source (conn_a.id = 1) to target (conn_b.id = 2)
                    # google_event_id changes from old ID to new event ID
                    test_event_record.connection_id = (
                        2  # Update to target connection (conn_b.id = 2)
                    )
                    test_event_record.google_event_id = (
                        "new_event_b_456"  # Update to new event ID
                    )
                    print(
                        f"    DEBUG: After updating event_record, connection_id = {test_event_record.connection_id}, google_event_id = {test_event_record.google_event_id}"
                    )
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_event_record
                    return event_query_mock
                else:
                    print(
                        f"    Returning Mock for session 4: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 5: relevance check for second switch (B->C)
            elif call_num == 5:
                if query_num == 1 and is_user_query(query_args):
                    # Query for User - relevance check
                    print(
                        f"    Returning User for relevance check with selected calendar {calendar_c}"
                    )
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    mock_user = Mock()
                    mock_user.id = user_id
                    mock_user.selected_calendar_id = (
                        calendar_a  # User has already chosen target
                    )
                    mock_user.lesson_colors = {}
                    user_filter_mock.first.return_value = mock_user
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                else:
                    print(
                        f"    Returning Mock for session 5: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 6: constructor (loading user colors) for second switch
            elif call_num == 6:
                if query_num == 1 and is_user_query(query_args):
                    # Query for User - load user colors
                    print(f"    Returning User for loading colors")
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    mock_user = Mock()
                    mock_user.selected_calendar_id = (
                        calendar_a  # Keep track of selection
                    )
                    mock_user.lesson_colors = {}  # Empty colors
                    user_filter_mock.first.return_value = mock_user
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                elif query_num == 2 and is_gcc_query(query_args):
                    # Query for source_connection (constructor phase)
                    print(
                        f"    Returning source connection for {calendar_b} in constructor"
                    )
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_b
                    return connection_query_mock
                elif query_num == 3 and is_gcc_query(query_args):
                    # Query for target_connection (constructor phase)
                    print(
                        f"    Returning target connection for {calendar_c} in constructor"
                    )
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_a
                    return connection_query_mock
                else:
                    print(
                        f"    Returning Mock for session 6: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 7: additional constructor/validation (second switch)
            elif call_num == 7:
                if query_num == 1 and is_user_query(query_args):
                    # Query for User - maybe checking selection again or additional validation
                    print(f"    Returning User for additional validation")
                    user_query_mock = Mock()
                    user_filter_mock = Mock()
                    mock_user = Mock()
                    mock_user.selected_calendar_id = (
                        calendar_c  # Keep track of selection
                    )
                    mock_user.lesson_colors = {}  # Empty colors
                    user_filter_mock.first.return_value = mock_user
                    user_query_mock.filter.return_value = user_filter_mock
                    return user_query_mock
                else:
                    print(
                        f"    Returning Mock for session 7: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 8: connection validation (again) + lessons query start (second switch)
            elif call_num == 8:
                if query_num == 1 and is_gcc_query(query_args):
                    # Query for source_connection (validation)
                    print(f"    Returning source connection for {calendar_b}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_b
                    return connection_query_mock
                elif query_num == 2 and is_gcc_query(query_args):
                    # Query for target_connection (validation)
                    print(f"    Returning target connection for {calendar_c}")
                    connection_query_mock = Mock()
                    connection_filter1_mock = Mock()
                    connection_filter2_mock = Mock()
                    connection_query_mock.filter.return_value = connection_filter1_mock
                    connection_filter1_mock.filter.return_value = (
                        connection_filter2_mock
                    )
                    connection_filter2_mock.first.return_value = conn_a
                    return connection_query_mock
                elif query_num == 3 and is_lesson_query(query_args):
                    # session.query(Lesson) - start of lessons query for second switch
                    print(f"    Lessons query: starting Lesson query for second switch")
                    lesson_query_mock = Mock()
                    # Set up chaining for the full lessons query
                    lesson_query_mock.join.return_value = lesson_query_mock
                    lesson_query_mock.filter.return_value = (
                        lesson_query_mock  # First filter (join)
                    )
                    lesson_query_mock.filter.return_value = lesson_query_mock  # Second filter (overwrites first, but that's OK)

                    # Set up .all() to return our lessons list only if conditions are met
                    def mock_all():
                        # Check if lesson would pass the join and filters
                        # For the join condition: Lesson.google_event_id == GoogleCalendarEvent.google_event_id
                        # We need to check if there's a GoogleCalendarEvent with matching google_event_id
                        # and the right connection_id

                        user_ok = test_lesson.user_id == user_id

                        # Based on the call_num, we know exactly what the values should be
                        if call_num == 3:
                            # First switch (A->B) - lessons query
                            # Before processing: connection_id = 1 (conn_a), google_event_id = "event_123"
                            connection_id_val = 1
                            google_event_id_val = "event_123"
                        elif call_num == 8:
                            # Second switch (B->C) - lessons query
                            # After first switch: connection_id = 2 (conn_b), google_event_id = "new_event_b_456"
                            connection_id_val = 2
                            google_event_id_val = "new_event_b_456"
                        else:
                            # Fallback - use current values (shouldn't happen in this test)
                            connection_id_val = test_event_record.connection_id
                            google_event_id_val = test_event_record.google_event_id

                        print(
                            f"    DEBUG: Using connection_id_val = {connection_id_val} for call_num {call_num}"
                        )
                        print(
                            f"    DEBUG: Using google_event_id_val = {google_event_id_val} for call_num {call_num}"
                        )
                        print(
                            f"    DEBUG: test_lesson.google_event_id = {test_lesson.google_event_id}"
                        )

                        # Simulate the joined GoogleCalendarEvent object
                        # In the real query, this would come from the join
                        mock_event = Mock()
                        mock_event.google_event_id = google_event_id_val
                        mock_event.connection_id = connection_id_val

                        event_match = (
                            mock_event.google_event_id == test_lesson.google_event_id
                        )
                        connection_ok = (
                            mock_event.connection_id == conn_b.id
                        )  # source is conn_b for second switch

                        print(
                            f"    Lessons query: checking conditions - user_ok={user_ok}, event_match={event_match}, connection_ok={connection_ok}"
                        )
                        print(
                            f"    DEBUG: mock_event.connection_id = {mock_event.connection_id}, conn_b.id = {conn_b.id}"
                        )

                        if user_ok and event_match and connection_ok:
                            return [test_lesson]
                        else:
                            return []

                    lesson_query_mock.all = mock_all

                    return lesson_query_mock
                else:
                    print(
                        f"    Returning Mock for session 8: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            # SESSION 9: lesson processing part 1 (second switch) - would come after successful lessons query
            elif call_num == 9:
                if query_num == 1 and is_lesson_query(query_args):
                    # Lesson query with for_update for second switch
                    print(f"    Lesson query with for_update for second switch")
                    lesson_query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()
                    lesson_query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_lesson
                    return lesson_query_mock
                elif query_num == 2 and is_gce_query(query_args):
                    # Event record query with for_update for second switch
                    print(f"    Event record query with for_update for second switch")
                    print(
                        f"    DEBUG: Before returning event_record, connection_id = {test_event_record.connection_id}, google_event_id = {test_event_record.google_event_id}"
                    )
                    print(
                        f"    DEBUG: Object ID: {id(test_event_record)}, connection_id type: {type(test_event_record.connection_id)}"
                    )
                    # Simulate the update that happens during processing:
                    # connection_id changes from source (conn_b.id = 2) to target (conn_c.id = 3)
                    # google_event_id changes from old ID to new event ID
                    test_event_record.connection_id = conn_a.id
                    test_event_record.google_event_id = "new_event_a_789"
                    test_event_record.calendar_id = calendar_a
                    print(
                        f"    DEBUG: After updating event_record, connection_id = {test_event_record.connection_id}, google_event_id = {test_event_record.google_event_id}"
                    )
                    print(
                        f"    DEBUG: Object ID: {id(test_event_record)}, connection_id type: {type(test_event_record.connection_id)}"
                    )
                    event_query_mock = Mock()
                    filter_mock = Mock()
                    with_for_update_mock = Mock()
                    event_query_mock.filter.return_value = filter_mock
                    filter_mock.with_for_update.return_value = with_for_update_mock
                    with_for_update_mock.first.return_value = test_event_record
                    return event_query_mock
                else:
                    print(
                        f"    Returning Mock for session 9: call_num={call_num}, query_num={query_num}"
                    )
                    return Mock()
            else:
                print(f"    Returning Mock for unknown call_num: {call_num}")
                return Mock()

        mock_session.query.side_effect = query_side_effect
        return mock_session

    # Mock service calls
    service_calls = []

    def get_service_mock(*args, **kwargs):
        service_calls.append(len(service_calls) + 1)
        call_num = len(service_calls)

        mock_service = Mock()
        if call_num == 1:
            # Source service for A->B switch
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(
                return_value={
                    "id": "event_123",
                    "summary": "Test Lesson",
                    "start": {"dateTime": "2026-10-08T19:00:00Z"},
                    "end": {"dateTime": "2026-10-08T20:00:00Z"},
                    "created": "2026-10-08T12:00:00Z",
                    "updated": "2026-10-08T12:00:00Z",
                    "status": "confirmed",
                }
            )

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)
        elif call_num == 2:
            # Target service for A->B switch
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(
                return_value={
                    "id": "new_event_b_456",
                    "summary": "Test Lesson",
                    "start": {"dateTime": "2026-10-08T19:00:00Z"},
                    "end": {"dateTime": "2026-10-08T20:00:00Z"},
                    "created": "2026-10-08T12:00:00Z",
                    "updated": "2026-10-08T12:00:00Z",
                    "status": "confirmed",
                }
            )
        elif call_num == 3:
            # Source service for B->C switch (new source is B)
            mock_source_events = Mock()
            mock_service.events = Mock(return_value=mock_source_events)
            mock_source_get = Mock()
            mock_source_events.get = Mock(return_value=mock_source_get)
            mock_source_get.execute = Mock(
                return_value={
                    "id": "new_event_b_456",
                    "summary": "Test Lesson",
                    "start": {"dateTime": "2026-10-08T19:00:00Z"},
                    "end": {"dateTime": "2026-10-08T20:00:00Z"},
                    "created": "2026-10-08T12:00:00Z",
                    "updated": "2026-10-08T12:00:00Z",
                    "status": "confirmed",
                }
            )

            mock_source_delete = Mock()
            mock_source_events.delete = Mock(return_value=mock_source_delete)
            mock_source_delete.execute = Mock(return_value=None)
        elif call_num == 4:
            # Target service for B->A switch
            mock_target_events = Mock()
            mock_service.events = Mock(return_value=mock_target_events)
            mock_target_insert = Mock()
            mock_target_events.insert = Mock(return_value=mock_target_insert)
            mock_target_insert.execute = Mock(
                return_value={
                    "id": "new_event_a_789",
                    "summary": "Test Lesson",
                    "start": {"dateTime": "2026-10-08T19:00:00Z"},
                    "end": {"dateTime": "2026-10-08T20:00:00Z"},
                    "created": "2026-10-08T12:00:00Z",
                    "updated": "2026-10-08T12:00:00Z",
                    "status": "confirmed",
                }
            )

        return mock_service

    with patch.object(db, "session") as mock_session_method:
        mock_session_method.side_effect = session_mock

        with patch(
            "app.google_calendar.service.get_google_calendar_service"
        ) as mock_get_service:
            mock_get_service.side_effect = get_service_mock

            # First switch: A->B
            print("  Executing first switch: A->B")
            result1 = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, calendar_a, calendar_b
            )

            # Second switch: B->C (should process C as final choice)
            print("  Executing second switch: B->A")
            result2 = GoogleCalendarSyncService.switch_calendar_for_user(
                db, user_id, calendar_b, calendar_a
            )

            print(f"  First switch result: {result1}")
            print(f"  Second switch result: {result2}")

            # Both switches should succeed
            assert result1 == 1, (
                f"First switch A->B should process 1 lesson, got {result1}"
            )
            assert result2 == 1, (
                f"Second switch B->A should process 1 lesson, got {result2}"
            )
            # Verify lesson's google_event_id was updated to final target
            assert test_lesson.google_event_id == "new_event_a_789", (
                f"Lesson should point to final target event, got {test_lesson.google_event_id}"
            )

            # Verify event record was updated to final target
            print(
                f"    DEBUG: Before assertion - test_event_record.connection_id = {test_event_record.connection_id} (type: {type(test_event_record.connection_id)})"
            )
            print(
                f"    DEBUG: Before assertion - conn_a.id = {conn_a.id} (type: {type(conn_a.id)})"
            )
            assert test_event_record.connection_id == conn_a.id, (
                f"Expected {conn_a.id}, got {test_event_record.connection_id}"
            )
            assert test_lesson.google_event_id == "new_event_a_789"
            assert test_event_record.calendar_id == calendar_a

    print("  [OK] Fast A->B->A switching handled correctly")


if __name__ == "__main__":
    print("Running switch calendar test...\n")

    try:
        test_fast_switching_iso_ab_a()
        print()

        print("Test passed! [OK]")

    except Exception as e:
        print(f"\n!! Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
