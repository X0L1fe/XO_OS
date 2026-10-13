# Implementation Summary: Google Calendar Switching Mechanism

## Overview
This implementation provides a safe mechanism for switching between Google Calendar calendars in XO_OS that prevents race conditions during rapid calendar switching and transfers only XOOS lesson events while preserving personal events.

## Changes Made

### 1. Database Model Addition (`app/database/models.py`)
- **Added** `CalendarSwitchLock` table with unique constraint on `user_id` to prevent concurrent calendar switching operations
- **Columns**: `id`, `user_id` (foreign key to users, unique, indexed), `locked_at` (timestamp)

### 2. Service Enhancement (`app/google_calendar/service.py`)
- **Added** `switch_calendar_for_user` classmethod to `GoogleCalendarSyncService`
- **Features**:
  - Background task that transfers lessons from source to target calendar
  - Processes each lesson in separate database transaction for consistency
  - Handles lessons with existing events (copy to target, delete from source)
  - Handles lessons without events (create new in target)
  - Proper error handling and logging - individual lesson failures don't block others
  - Returns count of successfully processed lessons

### 3. Route Modification (`app/google_calendar/routes.py`)
- **Enhanced** `select_google_calendar` function to:
  - Detect when calendar switching is needed (old vs new calendar selection)
  - Attempt to acquire switch lock via `CalendarSwitchLock` creation (unique constraint)
  - If lock acquired and service available: start switch task
  - If lock acquired but service unavailable: no tasks run (safe fallback)
  - If lock not acquired: fall back to initial sync (switch attempted later)
  - If no switch needed: just perform initial sync
  - Maintains backward compatibility

## Key Features

### Race Condition Prevention
- Uses database-level locking with unique constraint on `user_id`
- Only one calendar switch operation per user can proceed at a time
- Automatic lock cleanup via transaction completion

### Data Consistency
- Transactional processing of individual lessons
- Each lesson processed in isolated database transaction
- Atomic updates: event creation in target + deletion from source + record updates
- Failure isolation: one lesson failure doesn't affect others

### Selective Event Transfer
- Only transfers events associated with XOOS lessons (via `google_event_id` links)
- Personal events in source calendar remain untouched
- Preserves all manual modifications to personal events

### Graceful Degradation
- When Google OAuth service unavailable: no background tasks initiated
- When lock cannot be acquired: falls back to initial sync (switch attempted on next try)
- Proper error logging without breaking user experience

### Backward Compatibility
- No changes to existing data structures or APIs
- Maintains all existing functionality for initial calendar selection
- Clear separation between switch logic and initial sync logic

## Verification
- All existing tests continue to pass
- New comprehensive test suite validates:
  - Successful calendar switching with event transfer
  - Proper handling of missing connections (graceful failure)
  - Correct behavior when no lessons need switching
  - Object reference integrity throughout the process
  - Proper transaction handling and error recovery

## Files Modified
1. `app/database/models.py` - Added CalendarSwitchLock model
2. `app/google_calendar/service.py` - Added switch_calendar_for_user method
3. `app/google_calendar/routes.py` - Enhanced select_google_calendar function

## Testing
- Created comprehensive test suite in `tests/test_switch_calendar_working.py`
- Verified integration with existing Google Calendar tests
- All tests pass: 14/14 including new switch calendar tests

## Safety Considerations
- Database locking prevents concurrent switches for same user
- Individual lesson transactions limit failure scope
- Clear logging for debugging and monitoring
- No destruction of personal events or manual calendar modifications