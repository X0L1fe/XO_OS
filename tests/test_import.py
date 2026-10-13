#!/usr/bin/env python3
"""Test import of Google Calendar service."""

try:
    from google_auth_oauthlib.flow import Flow
    print("google_auth_oauthlib.flow imported successfully")
except ImportError as e:
    print(f"Failed to import google_auth_oauthlib.flow: {e}")

try:
    from app.google_calendar.auth import (
        SCOPES,
        get_credentials_path,
        get_google_calendar_service,
        get_token_path,
    )
    print("app.google_calendar.auth imported successfully")
    print(f"get_google_calendar_service: {get_google_calendar_service}")
except ImportError as e:
    print(f"Failed to import app.google_calendar.auth: {e}")

try:
    from app.google_calendar.service import GoogleCalendarSyncService
    print("app.google_calendar.service imported successfully")
    print(f"GoogleCalendarSyncService: {GoogleCalendarSyncService}")
except ImportError as e:
    print(f"Failed to import app.google_calendar.service: {e}")