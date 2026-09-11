# XO_OS - MAISync Documentation

## Architecture Overview

XO_OS is a system for synchronizing academic schedules from ICS files (typically from MAI's timetable system) into a local SQLite database and optionally into Google Calendar.

### Main Components

1. **Telegram Bot** (`app/telegram_bot.py`):
   - Receives ICS files from users (uploads or forwarded messages).
   - Delegates the import process to the `xo-os import` CLI command.
   - Ensures that each file is processed only once (temporary files are cleaned up).

2. **Web API** (`app/main.py`):
   - Provides a RESTful endpoint (`/import-ics`) for importing ICS files via HTTP POST.
   - Also provides health check (`/health`), statistics (`/stats`), and Obsidian export (`/export`) endpoints.
   - Built with FastAPI.

3. **Command Line Interface (CLI)** (`app/main.py`):
   - Accessible via `xo-os` command (if installed) or `python -m app.main`.
   - Supports subcommands:
     - `import`: Import an ICS file from a given path.
     - `status`: Show the number of lessons in the local database.
     - `export`: Export all lessons to an Obsidian vault.
     - `stats`: Show user statistics and gamification data.

4. **Sync Service** (`app/sync/service.py`):
   - Core logic for parsing ICS files, calculating differences between existing and incoming lessons, and updating the local database.
   - Handles the creation, updating, moving, and deletion of lessons in the database.
   - Optionally synchronizes changes with Google Calendar via `GoogleCalendarSyncService`.
   - Updates user statistics and gamification data after each import.

5. **Google Calendar Service** (`app/google_calendar/service.py`):
   - Handles synchronization of lessons with Google Calendar.
   - Creates, updates, and deletes events in a specified Google Calendar.
   - Implements conflict detection and resolution (removes orphaned events, creates missing events).
   - Applies color coding to events based on lesson type:
     - ЛК (LECTURE): No color change (default).
     - ПЗ (PRACTICE): Grape (colorId = 3).
     - ЛР (LAB): Banana (colorId = 5).
     - Э (EXAM): Tomato (colorId = 11).
   - Implements incremental sync by comparing lesson content hashes to avoid unnecessary updates.

6. **Database Models** (`app/database/models.py`):
   - `Lesson`: Represents a single academic lesson with fields for timing, subject, type, category, teachers, room, etc.
     - Includes `content_hash` for detecting changes in lesson data.
     - Includes `google_event_id` to link to Google Calendar events.
     - Includes `last_synced_content_hash` and `last_synced_at` for incremental sync.
   - `UserStats`: Singleton table storing user's XP, streak, level, and last activity date for gamification.

7. **ICS Parser** (`app/ics/parser.py`):
   - Parses ICS files and extracts lesson data.
   - Normalizes lesson data into `LessonData` objects.
   - Computes a stable identity key (`identity_key`) based on date, time, subject, and category.
   - Detects lesson type and category from the description and subject.
   - Computes a content hash (`content_hash`) based on all changeable fields.

## API Description

### Web Endpoints

- `GET /health`
  - Returns: `{"status": "ok", "service": "XO_OS"}`
  - Description: Health check endpoint.

- `POST /import-ics`
  - Parameters:
    - `file` (required): The ICS file to import (multipart/form-data).
    - `calendar` (optional): Name of the Google Calendar to sync to. Defaults to the value of the `GOOGLE_CALENDAR_NAME` environment variable or "ВУЗ МАИ".
  - Returns (on success):
    ```json
    {
      "status": "success",
      "parsed": <int>,
      "created": <int>,
      "updated": <int>,
      "moved": <int>,
      "deleted": <int>,
      "unchanged": <int>,
      "message": "<string>"
    }
    ```
  - Returns (on error):
    ```json
    {
      "status": "error",
      "message": "<string>"
    }
    ```
  - Description: Imports an ICS file, updates the local database, and optionally synchronizes with Google Calendar.

- `POST /export`
  - Parameters:
    - `vault` (optional): Path to the Obsidian vault. Defaults to the value of the `OBSIDIAN_VAULT_PATH` environment variable.
  - Returns (on success):
    ```json
    {
      "status": "success",
      "exported": <int>,
      "message": "<string>"
    }
    ```
  - Returns (on error):
    ```json
    {
      "status": "error",
      "message": "<string>"
    }
    ```
  - Description: Exports all lessons to an Obsidian vault, creating markdown files in subdirectories by lesson type.

- `GET /stats` (not implemented in the provided code, but the CLI command exists)
  - Note: The web API does not currently include a `/stats` endpoint, but the CLI does. For consistency, one could be added.

### CLI Commands

- `xo-os import <path> [--calendar <name>]`
  - Imports the ICS file at `<path>`.
  - Optional `--calendar` specifies the Google Calendar name (defaults to environment variable or "ВУЗ МАИ").

- `xo-os status`
  - Prints the number of lessons in the local database.

- `xo-os export <vault_path>`
  - Exports all lessons to the Obsidian vault at `<vault_path>`.

- `xo-os stats`
  - Prints user statistics and gamification data:
    - Level
    - Total XP
    - Current streak (days)
    - Max streak (days)
    - Last activity date

### Environment Variables

- `TELEGRAM_BOT_TOKEN` (required for the Telegram bot): The token for the Telegram bot.
- `GOOGLE_CALENDAR_NAME` (optional): Default name of the Google Calendar to sync to. Defaults to "ВУЗ МАИ".
- `OBSIDIAN_VAULT_PATH` (optional): Default path to the Obsidian vault for export.

## User Guide

### Setting Up the Telegram Bot

1. Obtain a token from [BotFather](https://t.me/BotFather) for your bot.
2. Set the `TELEGRAM_BOT_TOKEN` environment variable to the token.
   - Optionally, set `GOOGLE_CALENDAR_NAME` if you want to use a calendar other than "ВУЗ МАИ".
3. Run the bot:
   ```bash
   python -m app.telegram_bot
   ```
   - Alternatively, if you have installed the package, you can run `xo-os-bot`.

4. In Telegram, send an ICS file to the bot (by uploading or forwarding from another bot like @Timetable_MAI_bot).
5. The bot will respond with the import result.

### Using the Web API

1. Start the FastAPI server (e.g., with Uvicorn):
   ```bash
   uvicorn app.main:app --reload
   ```
2. Send a POST request to `/import-ics` with an ICS file and optional `calendar` parameter.
3. Use the other endpoints as needed.

### Using the CLI

1. Ensure you are in the project directory and have the necessary dependencies installed.
2. Run commands with `python -m app.main <command> [options]`.
   - Example: `python -m app.main import path/to/schedule.ics --calendar "Личный календарь"`
   - Or, if you have set up an entry point (e.g., via `pip install -e .`), you can use `xo-os` directly.

### Obsidian Export

1. Set the `OBSIDIAN_VAULT_PATH` environment variable to the path of your Obsidian vault, or specify the path directly in the CLI or web endpoint.
2. Run the export command:
   ```bash
   python -m app.main export /path/to/your/vault
   ```
   - This will create a folder structure in your vault:
     ```
     /path/to/your/vault/
       LECTURE/
         <identity_key>.md
       PRACTICE/
         <identity_key>.md
       LAB/
         <identity_key>.md
       EXAM/
         <identity_key>.md
       OTHER/
         <identity_key>.md
     ```
   - Each markdown file contains the lesson details.

### Statistics and Gamification

- The system tracks:
  - **XP (Experience Points)**: Earned at a rate of 10 XP per lesson imported.
  - **Level**: Calculated as `(total_xp // 1000) + 1`.
  - **Current Streak**: Number of consecutive days with at least one lesson import.
  - **Max Streak**: The highest current streak achieved.
- Statistics are stored in the `user_stats` table (singleton row with `id=1`).
- View statistics via the CLI command `xo-os stats`.

### Notes on Incremental Sync

- The system avoids unnecessary updates to Google Calendar by comparing the `content_hash` of each lesson with the `last_synced_content_hash` stored in the database.
- If the hashes match, the lesson is considered unchanged and the Google Calendar event is not updated.
- This reduces the number of API calls to Google Calendar and prevents unnecessary modifications.

### Conflict Resolution

- The Google Calendar service periodically checks for conflicts:
  - Events in Google Calendar that do not have a corresponding local lesson are deleted.
  - Local lessons that have a `google_event_id` but no corresponding event in Google Calendar are (re)created.
- This ensures that the Google Calendar stays in sync with the local database, even if manual changes were made in the calendar.

## Dependencies

- Python 3.9+
- Required Python packages are listed in `requirements.txt` (if present) or can be inferred from the imports:
  - `python-telegram-bot`
  - `python-dotenv`
  - `google-api-python-client`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
  - `icalendar`
  - `fastapi`
  - `uvicorn`
  - `SQLAlchemy`

## License

This project is proprietary and intended for personal use with MAI's timetable system.