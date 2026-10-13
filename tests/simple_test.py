#!/usr/bin/env python3
"""Simple test to verify the method exists and can be called."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.google_calendar.service import GoogleCalendarSyncService
from app.database.db import Database

print("Testing basic method call...")

# Create a mock database
db = Database()

# Try to call the method with minimal parameters
try:
    result = GoogleCalendarSyncService.switch_calendar_for_user(
        db,
        user_id=1,
        source_calendar_id="source",
        target_calendar_id="target"
    )
    print(f"Method returned: {result}")
except Exception as e:
    print(f"Method raised exception: {e}")
    import traceback
    traceback.print_exc()