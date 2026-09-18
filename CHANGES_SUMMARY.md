# Changes Made for MAIS Schedule Parser Layer

## 1. Google Calendar Service Formatting (`app/google_calendar/service.py`)
- Added `LESSON_TYPE_ABBREVIATION_MAP` to map lesson types to Russian abbreviations:
  - LECTURE → "ЛК"
  - PRACTICE → "ПЗ"
  - LAB → "ЛР"
  - EXAM → "Э"
- Modified `_lesson_to_google_event` function to:
  - Set event title (`summary`) as: `{abbreviation} {subject}` (e.g., "ЛК Математика")
  - Set event description (`description`) as: room on first line, teacher on second line (if present)
  - Cleared the `location` field (set to empty string) as per requirements
  - Kept existing color mapping and reminders

## 2. Database Model Extensions (`app/database/models.py`)
### User Model Additions:
- `mais_group_id`: String column to store the user's MAIS group identifier
- `notifications_enabled`: Integer column (0/1) to enable/disable schedule change notifications
- `last_mais_check`: DateTime column to track when we last checked for MAIS schedule changes
- `notifications`: Relationship to Notification model (one-to-many)

### Notification Model:
- `id`: Primary key
- `user_id`: Foreign key to User
- `title`: Notification title (e.g., "Изменения в расписании")
- `message`: Detailed message about changes
- `is_read`: Boolean (stored as Integer) to track read status
- `type`: Notification type (e.g., "schedule_change")
- `related_id`: ID of related entity (e.g., lesson ID)
- `related_type`: Type of related entity (e.g., "lesson")
- `created_at`: Timestamp when notification was created
- Relationship to User (many-to-one)

## 3. Background Task for Periodic Checking (`app/main.py`)
Added:
- `check_mais_schedule_for_user(user, session)`: 
  - Fetches schedule for user's MAIS group using asynchronous HTTP client
  - Parses schedule into LessonData objects
  - Imports lessons via SyncService (which syncs with Google Calendar)
  - If changes detected (created/updated/moved/deleted > 0):
    - Creates a Notification record in the database
    - Sends Telegram notification if user has Telegram linked and notifications enabled
- `periodic_mais_check()`:
  - Runs in loop with 1-hour interval
  - Fetches all users with MAIS group set and notifications enabled
  - For each user, checks if it's time to run (based on `last_mais_check`)
  - Executes `check_mais_schedule_for_user` and updates `last_mais_check`
- Startup event handler that launches `periodic_mais_check` as a background task

## 4. API Endpoints (`app/main.py`)
### Notifications:
- `GET /api/notifications`: Returns list of notifications for current user (newest first)
- `POST /api/notifications/{notification_id}/read`: Marks notification as read
### Settings:
- `POST /api/notifications/toggle`: Toggles notifications enabled for current user
### MAIS Group:
- `POST /api/mais/group`: Sets the MAIS group for current user (takes `group_name` as form parameter)

## 5. MAIS Parser Enhancements (`app/mais_parser.py`)
- Added `async_fetch_groups()` and `async_fetch_group_schedule()` functions using `httpx.AsyncClient`
- Used by background task for non-blocking HTTP requests

## 6. Imports and Dependencies (`app/main.py`)
- Added imports for `httpx`, `List` from typing, and `Session` from sqlalchemy.orm
- Fixed potential naming conflict by renaming SQLAlchemy Session import
- Imported User, Notification, Lesson, UserStats from app.database.models

## How It Works
1. User sets their MAIS group via `/api/mais/group` (or implicitly when importing a schedule)
2. Background task runs every hour (configurable in code)
3. For each user with notifications enabled:
   - Fetches latest schedule from MAIS public API
   - Compares with current lessons in database via SyncService
   - If changes found:
     - Creates notification in database
     - Sends Telegram alert (if linked)
4. User can view notifications via `/api/notifications` and mark as read
5. User can toggle notifications on/off via `/api/notifications/toggle`

## Notes
- The background task uses a 1-hour interval (3600 seconds) - can be adjusted in `periodic_mais_check()`
- Notifications are stored in the database and can be fetched by the frontend for display
- Telegram notifications require the user to have linked their Telegram account via existing `/api/telegram/link` endpoint
- The Google Calendar event formatting now strictly follows the user's requirements:
  - Title: Lesson type abbreviation (ЛК/ПЗ/ЛР/Э) + space + subject name
  - Description: Room on first line, teacher on second line (empty lines omitted if missing)
  - Location field is left empty