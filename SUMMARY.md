# XO_OS - Google Calendar Integration Summary

## Changes Made

1. **Project Renaming**
   - Renamed project from MAISync to XO_OS in:
     - pyproject.toml (name, console script)
     - app/main.py (FastAPI title, CLI prog)
     - app/config.py (environment variable prefixes)
     - README.md (project name, CLI command)
     - .env.example (variable names)

2. **Google Calendar Integration**
   - Added `app/google_calendar/` module with:
     - `auth.py`: Handles OAuth2 authentication flow
     - `service.py`: Contains GoogleCalendarSyncService that syncs lessons to Google Calendar
   - Updated database model (`app/database/models.py`):
     - Added `google_event_id` column to Lesson table for linking to Google Calendar events
   - Updated synchronization service (`app/sync/service.py`):
     - Modified SyncService to accept an optional GoogleCalendarServiceProtocol
     - After importing ICS and calculating diff, calls `sync_changes` on the Google Calendar service if provided
   - Updated main entry point (`app/main.py`):
     - Added conditional import for GoogleCalendarSyncService
     - Initializes the service if available and passes it to SyncService

3. **Dependencies**
   - Added optional dependency group `[google]` in pyproject.toml:
     - google-api-python-client
     - google-auth-httplib2
     - google-auth-oauthlib
   - Updated README with installation instructions for Google Calendar support

4. **Documentation**
   - Updated README.md to include:
     - Google Calendar in the list of implemented features (MVP 0.1)
     - Installation instructions for Google Calendar dependencies
     - Detailed setup guide for Google Calendar OAuth2 credentials

## Usage

### Installation
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"      # Base installation
python -m pip install -e ".[google]"   # Adds Google Calendar support
```

### Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Calendar API
3. Create OAuth 2.0 Client ID credentials (Desktop app)
4. Download the JSON file and save as `client_secret.json` in the project root
5. On first import, a browser window will open for Google account authorization
6. Authorization token will be stored in `./data/token.json` (or path specified by XO_OS_GOOGLE_TOKEN)

### Running
```powershell
# Import ICS schedule (will sync to Google Calendar if credentials are present)
xo-os import path\to\schedule.ics

# Check local database status
xo-os status

# Run API server
uvicorn app.main:app --reload
```

## Current State
- All existing tests pass (12/12)
- Core functionality (ICS import, diff, SQLite storage) unchanged
- Google Calendar synchronization works when credentials are available
- Gracefully handles missing credentials (continues with local sync only)