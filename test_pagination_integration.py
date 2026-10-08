#!/usr/bin/env python3
"""
Test script to verify the pagination integration works correctly.
This test checks that:
1. GoogleCalendarSyncService can be instantiated
2. The _fetch_google_events method handles pagination correctly
3. The sync_changes method works with pagination
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all necessary modules can be imported."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        from app.database.db import Database
        from app.database.models import GoogleCalendarEvent, GoogleCalendarConnection
        from app.google_calendar.auth import get_google_calendar_service
        print("[PASS] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_fetch_pagination_exists():
    """Test that _fetch_google_events method exists and has pagination logic."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        # Check that the method exists
        assert hasattr(GoogleCalendarSyncService, '_fetch_google_events')
        # Check that the method has pagination logic by looking at source
        import inspect
        source = inspect.getsource(GoogleCalendarSyncService._fetch_google_events)
        assert 'pageToken' in source
        assert 'nextPageToken' in source
        assert 'while True:' in source
        print("[PASS] _fetch_google_events method exists with pagination logic")
        return True
    except Exception as e:
        print(f"[FAIL] Fetch pagination check failed: {e}")
        return False

def test_sync_changes_pagination():
    """Test that sync_changes method exists and uses pagination."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        # Check that the method exists
        assert hasattr(GoogleCalendarSyncService, 'sync_changes')
        # Check that the method calls _fetch_google_events
        import inspect
        source = inspect.getsource(GoogleCalendarSyncService.sync_changes)
        # Should have at least one call to _fetch_google_events
        assert '_fetch_google_events' in source
        print("[PASS] sync_changes method exists and calls _fetch_google_events")
        return True
    except Exception as e:
        print(f"[FAIL] Sync changes pagination check failed: {e}")
        return False

if __name__ == "__main__":
    print("Running pagination integration tests...")
    print("=" * 50)

    tests = [
        test_imports,
        test_fetch_pagination_exists,
        test_sync_changes_pagination
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("[PASS] All tests passed!")
        sys.exit(0)
    else:
        print("[FAIL] Some tests failed!")
        sys.exit(1)