#!/usr/bin/env python3
"""
Test that _detect_and_handle_conflicts calls _fetch_google_events when google_events is None.
"""

import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

def test_fetch_called_when_none():
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(sync_service, '_fetch_google_events', return_value=[{"id": "1"}]) as mock_fetch:
        # Call with google_events=None (default)
        sync_service._detect_and_handle_conflicts(service_mock, google_events=None)
        mock_fetch.assert_called_once_with(service_mock)
        print("[PASS] _fetch_google_events called when google_events is None")

def test_fetch_not_called_when_provided():
    db = Database()
    service_mock = Mock()
    sync_service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

    with patch.object(sync_service, '_fetch_google_events') as mock_fetch:
        # Call with google_events provided
        sync_service._detect_and_handle_conflicts(service_mock, google_events=[{"id": "2"}])
        mock_fetch.assert_not_called()
        print("[PASS] _fetch_google_events NOT called when google_events provided")

if __name__ == "__main__":
    print("Testing that _detect_and_handle_conflicts correctly handles google_events parameter...")
    print("=" * 70)
    test_fetch_called_when_none()
    test_fetch_not_called_when_provided()
    print("=" * 70)
    print("All tests passed.")