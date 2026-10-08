#!/usr/bin/env python3
"""Test the signature of _detect_and_handle_conflicts."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

# Create a dummy service and db
db = Database()
# We don't need to initialize the db fully for this test.
service = GoogleCalendarSyncService(db, user_id=1, calendar_id="primary")

# Check the method signature
import inspect
sig = inspect.signature(service._detect_and_handle_conflicts)
print("Signature:", sig)

# Try to call with the extra parameter
try:
    # We cannot actually call it because we don't have a real Google service,
    # but we can check if it accepts the parameter by trying to bind.
    # We'll bind the arguments we would pass: service and google_events=some_list
    # We'll pass a dummy service (can be None) and a dummy list.
    bound = sig.bind(service, google_events=[])
    print("Binding succeeded: the method accepts google_events parameter")
except TypeError as e:
    print("Binding failed:", e)
    print("The method does not accept the google_events parameter")