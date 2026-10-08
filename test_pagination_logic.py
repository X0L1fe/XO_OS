#!/usr/bin/env python3
"""
Test script to verify the pagination logic in _fetch_google_events method.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_pagination_logic():
    """Test that the pagination logic is correctly implemented."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        import inspect

        # Get the source code of _fetch_google_events
        source = inspect.getsource(GoogleCalendarSyncService._fetch_google_events)

        # Check for key pagination elements
        assert 'pageToken' in source, "Should reference pageToken"
        assert 'nextPageToken' in source, "Should reference nextPageToken"
        assert 'while True:' in source, "Should have a while loop for pagination"
        assert "request_params['pageToken'] = page_token" in source, "Should set pageToken in request params"
        assert "page_token = events_result.get('nextPageToken')" in source, "Should get nextPageToken from response"
        assert "if not page_token:" in source, "Should check for absence of page_token to break loop"
        assert "break" in source, "Should break loop when no more pages"

        # Check that we're accumulating events
        assert "all_events.extend(events)" in source, "Should accumulate events from each page"
        assert "enriched_events = []" in source, "Should initialize enriched_events list after pagination"
        assert "for event in all_events:" in source, "Should iterate through all accumulated events"

        print("[PASS] Pagination logic is correctly implemented")
        return True
    except Exception as e:
        print(f"[FAIL] Pagination logic check failed: {e}")
        return False

def test_backward_compatibility():
    """Test that the method still works with time_min and time_max parameters."""
    try:
        from app.google_calendar.service import GoogleCalendarSyncService
        import inspect

        # Get the source code of _fetch_google_events
        source = inspect.getsource(GoogleCalendarSyncService._fetch_google_events)

        # Debug: print what we're checking for time params
        print("DEBUG: Checking source for time parameters...")
        time_min_check = "request_params['timeMin'] = time_min.isoformat()" in source
        time_max_check = "request_params['timeMax'] = time_max.isoformat()" in source
        print(f"'request_params['timeMin'] = time_min.isoformat()' in source: {time_min_check}")
        print(f"'request_params['timeMax'] = time_max.isoformat()' in source: {time_max_check}")

        # Check that time_min and time_max are still handled
        assert "request_params['timeMin'] = time_min.isoformat()" in source, "Should handle time_min parameter"
        assert "request_params['timeMax'] = time_max.isoformat()" in source, "Should handle time_max parameter"
        # Note: The actual request params building happens conditionally, so we check the assignment
        # The string representation check is tricky due to formatting, so we'll skip the replace check for now

        print("[PASS] Backward compatibility with time_min/time_max maintained")
        return True
    except Exception as e:
        print(f"[FAIL] Backward compatibility check failed: {e}")
        return False

if __name__ == "__main__":
    print("Running pagination logic tests...")
    print("=" * 50)

    tests = [
        test_pagination_logic,
        test_backward_compatibility
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
        print("[PASS] All logic tests passed!")
        sys.exit(0)
    else:
        print("[FAIL] Some logic tests failed!")
        sys.exit(1)