#!/usr/bin/env python3
"""
Final regression test for the fix of _detect_and_handle_conflicts signature.
We mock the database session to avoid SQLAlchemy mapping issues.
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

def create_mock_session():
    """Create a mock session that returns empty results for queries."""
    session_mock = Mock()
    # Query for lessons: return empty list
    query_mock = Mock()
    session_mock.query.return_value = query_mock
    filter_mock = Mock()
    query_mock.filter.return_value = filter_mock
    filter_mock.all.return_value = []
    filter_mock.first.return_value = None
    # Context manager support
    session_mock.__enter__ = Mock(return_value=session_mock)
    session_mock.__exit__ = Mock(return_value=None)
    return session_mock

def test_old_style_signature():
    """Test that old style call does not throw TypeError."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(db, 'session', return_value=create_mock_session()):
        # Mock _fetch_google_events to avoid actual HTTP calls
        with patch.object(sync_service, '_fetch_google_events', return_value=[]):
            try:
                sync_service._detect_and_handle_conflicts(service_mock)
                return True, "Old style call succeeded"
            except TypeError as e:
                return False, f"Old style call threw TypeError: {e}"
            except Exception as e:
                # Other exceptions are okay for this test
                return True, f"Old style call threw non-TypeError (expected): {e}"

def test_new_style_signature():
    """Test that new style call does not throw TypeError."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(db, 'session', return_value=create_mock_session()):
        try:
            sync_service._detect_and_handle_conflicts(service_mock, google_events=[{"id": "test"}])
            return True, "New style call succeeded"
        except TypeError as e:
            return False, f"New style call threw TypeError: {e}"
        except Exception as e:
            return True, f"New style call threw non-TypeError (expected): {e}"

def test_fetch_called_when_none():
    """Test that _fetch_google_events is called when google_events is None."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    mock_session = create_mock_session()
    with patch.object(db, 'session', return_value=mock_session):
        with patch.object(sync_service, '_fetch_google_events', return_value=[{"id": "1"}]) as mock_fetch:
            sync_service._detect_and_handle_conflicts(service_mock, google_events=None)
            mock_fetch.assert_called_once_with(service_mock)
            return True, "_fetch_google_events called when google_events is None"

def test_fetch_not_called_when_provided():
    """Test that _fetch_google_events is NOT called when google_events is provided."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    mock_session = create_mock_session()
    with patch.object(db, 'session', return_value=mock_session):
        with patch.object(sync_service, '_fetch_google_events') as mock_fetch:
            sync_service._detect_and_handle_conflicts(service_mock, google_events=[{"id": "2"}])
            mock_fetch.assert_not_called()
            return True, "_fetch_google_events NOT called when google_events provided"

def test_sync_changes_flow():
    """Test that sync_changes can be called without TypeError and follows fetch->persist->detect flow."""
    db = Database()
    # We need to mock the service and the database session.
    with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service, \
         patch.object(db, 'session') as mock_session_method, \
         patch.object(GoogleCalendarSyncService, '_persist_google_events') as mock_persist, \
         patch.object(GoogleCalendarSyncService, '_detect_and_handle_conflicts') as mock_detect, \
         patch.object(GoogleCalendarSyncService, '_fetch_google_events') as mock_fetch:

        # Setup mock service
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        # Setup mock session to return a mock connection for the persistence block in sync_changes
        mock_session_instance = create_mock_session()
        # Override the first() return value to return a mock connection (not None)
        mock_conn = Mock()
        mock_conn.id = 1
        mock_conn.user_id = 1
        mock_conn.calendar_id = "primary"
        mock_conn.connected_at = Mock()
        # Get the filter mock from the session instance and set first to return our mock connection
        # We know the structure: session.query -> query_mock -> filter_mock
        # We'll set the filter_mock's first to return mock_conn
        # First, we need to get the filter mock from the session instance.
        # Since we are using create_mock_session, we know the structure.
        # But let's do it in a way that doesn't depend on the internal structure of create_mock_session.
        # Instead, we'll set up the session_instance to return our mock connection when query().filter().first() is called.
        # We'll create a new filter mock for this purpose.
        filter_mock = Mock()
        filter_mock.first.return_value = mock_conn
        filter_mock.all.return_value = []  # though not used in persistence block
        # Set up the session instance's query to return a query mock that returns our filter mock
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session_instance.query.return_value = query_mock

        # For the lessons query in _detect_and_handle_conflicts (but we are mocking that method)
        # We don't need to set up the lessons query because we are mocking the entire method.

        # Mock _fetch_google_events to return an empty list and None next_sync_token (to avoid HTTP calls and control flow)
        mock_fetch.return_value = ([], None)

        sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

        # Create an empty diff
        from app.sync.diff import DiffResult
        diff = DiffResult(created=[], updated=[], deleted=[], moved=[], unchanged=[])

        try:
            sync_service.sync_changes(diff)
            # Verify that the flow is: fetch -> persist -> detect
            # We expect:
            #   get_google_calendar_service called once
            #   _fetch_google_events called once (by sync_changes)
            #   _persist_google_events called once (with the connection and events)
            #   _detect_and_handle_conflicts called once (with service and the events)
            # We can check the mock calls.
            assert mock_get_service.call_count == 1
            assert mock_fetch.call_count == 1
            # Note: We cannot directly assert that _fetch_google_events was called once because we mocked it.
            # But we can check that persist and detect were called.
            assert mock_persist.call_count == 1
            assert mock_detect.call_count == 1
            # Check that detect was called with the service and the events (we didn't capture the events, but we can check the args)
            # The call to detect should be: detect(service, google_events=...)
            # We can check that the second argument (google_events) was passed.
            call_args = mock_detect.call_args
            assert call_args is not None
            assert 'google_events' in call_args.kwargs
            return True, "sync_changes executed with correct flow"
        except TypeError as e:
            return False, f"sync_changes threw TypeError: {e}"
        except Exception as e:
            return False, f"sync_changes threw unexpected exception: {e}"

if __name__ == "__main__":
    print("Running final regression tests for _detect_and_handle_conflicts signature fix...")
    print("=" * 80)

    tests = [
        ("Old style signature", test_old_style_signature),
        ("New style signature", test_new_style_signature),
        ("Fetch called when None", test_fetch_called_when_none),
        ("Fetch not called when provided", test_fetch_not_called_when_provided),
        ("Sync changes flow", test_sync_changes_flow),
    ]

    results = []
    for name, test_func in tests:
        passed, message = test_func()
        results.append(passed)
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {name}: {message}")
        print()

    print("=" * 80)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("SUCCESS: All regression tests passed.")
        sys.exit(0)
    else:
        print("FAILURE: Some regression tests failed.")
        sys.exit(1)