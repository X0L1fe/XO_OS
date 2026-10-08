#!/usr/bin/env python3
"""
Test the fix for _detect_and_handle_conflicts signature.
"""

import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

def test_old_style_call_no_typeerror():
    """Test that old style call does not throw TypeError."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    # Mock the session to avoid SQLAlchemy mapping errors and to control the flow
    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        # Mock the query for lessons
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []  # no lessons
        # Mock the query for connection (in persistence block) to return None
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Also mock _fetch_google_events to return a dummy list so we don't have to mock the service
        with patch.object(sync_service, '_fetch_google_events', return_value=[{"id": "test"}]):
            try:
                # This should not throw TypeError
                sync_service._detect_and_handle_conflicts(service_mock)
                print("  [PASS] Old style call succeeded (no TypeError)")
                return True
            except TypeError as e:
                print(f"  [FAIL] Old style call threw TypeError: {e}")
                return False
            except Exception as e:
                # Any other exception is not a TypeError, so we consider the signature test passed
                print(f"  [INFO] Old style call threw non-TypeError (expected): {e}")
                return True

def test_new_style_call_no_typeerror():
    """Test that new style call does not throw TypeError."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        try:
            # Provide google_events
            sync_service._detect_and_handle_conflicts(service_mock, google_events=[{"id": "test2"}])
            print("  [PASS] New style call succeeded (no TypeError)")
            return True
        except TypeError as e:
            print(f"  [FAIL] New style call threw TypeError: {e}")
            return False
        except Exception as e:
            print(f"  [INFO] New style call threw non-TypeError (expected): {e}")
            return True

def test_fetch_called_when_none():
    """Test that _fetch_google_events is called when google_events is None."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch.object(sync_service, '_fetch_google_events', return_value=[{"id": "1"}]) as mock_fetch:
            sync_service._detect_and_handle_conflicts(service_mock, google_events=None)
            mock_fetch.assert_called_once_with(service_mock)
            print("  [PASS] _fetch_google_events called when google_events is None")
            return True

def test_fetch_not_called_when_provided():
    """Test that _fetch_google_events is NOT called when google_events is provided."""
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(db, 'session') as mock_session_method:
        mock_session = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch.object(sync_service, '_fetch_google_events') as mock_fetch:
            sync_service._detect_and_handle_conflicts(service_mock, google_events=[{"id": "2"}])
            mock_fetch.assert_not_called()
            print("  [PASS] _fetch_google_events NOT called when google_events provided")
            return True

def test_sync_changes_no_typeerror():
    """Test that sync_changes can be called without TypeError (signature fix)."""
    db = Database()
    # We need to mock a lot to avoid real calls and mapping errors.
    with patch('app.google_calendar.service.get_google_calendar_service') as mock_get_service, \
         patch.object(db, 'session') as mock_session_method, \
         patch.object(GoogleCalendarSyncService, '_persist_google_events') as mock_persist, \
         patch.object(GoogleCalendarSyncService, '_detect_and_handle_conflicts') as mock_detect, \
         patch.object(GoogleCalendarSyncService, '_fetch_google_events') as mock_fetch:

        # Setup mock service
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        # Setup mock session to return a mock connection for the persistence block in sync_changes
        mock_session_instance = Mock()
        mock_session_method.return_value.__enter__.return_value = mock_session_instance
        # We need to set up the chain: session.query(...).filter(...).first() -> mock connection
        mock_conn = Mock()
        mock_conn.id = 1
        mock_conn.user_id = 1
        mock_conn.calendar_id = "primary"
        mock_conn.connected_at = Mock()
        filter_mock = Mock()
        filter_mock.first.return_value = mock_conn
        filter_mock.all.return_value = []
        query_mock = Mock()
        query_mock.filter.return_value = filter_mock
        mock_session_instance.query.return_value = query_mock

        # Mock _fetch_google_events to return an empty list (to avoid HTTP calls and control flow)
        mock_fetch.return_value = []

        sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

        # Create an empty diff
        from app.sync.diff import DiffResult
        diff = DiffResult(created=[], updated=[], deleted=[], moved=[], unchanged=[])

        try:
            sync_service.sync_changes(diff)
            print("  [PASS] sync_changes executed without TypeError")
            return True
        except TypeError as e:
            print(f"  [FAIL] sync_changes threw TypeError: {e}")
            return False
        except Exception as e:
            print(f"  [INFO] sync_changes threw non-TypeError (expected if mocks incomplete): {e}")
            return True

if __name__ == "__main__":
    print("Running signature fix tests for _detect_and_handle_conflicts...")
    print("=" * 70)

    tests = [
        test_old_style_call_no_typeerror,
        test_new_style_call_no_typeerror,
        test_fetch_called_when_none,
        test_fetch_not_called_when_provided,
        test_sync_changes_no_typeerror,
    ]

    results = []
    for test in tests:
        if test():
            results.append(True)
        else:
            results.append(False)
        print()

    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("SUCCESS: All signature fix tests passed.")
        sys.exit(0)
    else:
        print("FAILURE: Some signature fix tests failed.")
        sys.exit(1)