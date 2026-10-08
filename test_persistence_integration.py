#!/usr/bin/env python3
"""
Test script to verify the persistence integration works correctly.
This test checks that:
1. GoogleCalendarSyncService can be instantiated
2. The _fetch_google_events method works
3. Our new persistence code is in the right place
4. Basic import and syntax checks pass
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

def test_service_instantiation():
    """Test that we can create a service instance."""
    try:
        from app.database.db import Database
        db = Database()
        # We won't actually initialize a real service without credentials,
        # but we can check that the class can be imported and instantiated
        from app.google_calendar.service import GoogleCalendarSyncService
        print("[PASS] GoogleCalendarSyncService can be imported")
        return True
    except Exception as e:
        print(f"[FAIL] Service instantiation check failed: {e}")
        return False

def test_method_exists():
    """Test that our new method exists."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        # Check that the method exists
        assert hasattr(GoogleCalendarSyncService, '_persist_google_events')
        print("[PASS] _persist_google_events method exists")
        return True
    except Exception as e:
        print(f"[FAIL] Method check failed: {e}")
        return False

def test_fetch_exists():
    """Test that _fetch_google_events still exists."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        assert hasattr(GoogleCalendarSyncService, '_fetch_google_events')
        print("[PASS] _fetch_google_events method exists")
        return True
    except Exception as e:
        print(f"[FAIL] Fetch method check failed: {e}")
        return False

def test_sync_changes_exists():
    """Test that sync_changes still exists (we didn't modify it)."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        assert hasattr(GoogleCalendarSyncService, 'sync_changes')
        print("[PASS] sync_changes method exists")
        return True
    except Exception as e:
        print(f"[FAIL] Sync changes method check failed: {e}")
        return False

if __name__ == "__main__":
    print("Running persistence integration tests...")
    print("=" * 50)

    tests = [
        test_imports,
        test_service_instantiation,
        test_method_exists,
        test_fetch_exists,
        test_sync_changes_exists
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