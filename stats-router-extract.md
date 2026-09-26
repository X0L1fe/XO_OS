---
name: stats-router-extract
description: Extract stats router from main.py to app/stats/routes.py
metadata:
  type: project
---

## Summary

Extracted stats endpoints and helper functions from `app/main.py` into a modular structure:
- Created `app/stats/routes.py` containing all stats API endpoints (`/`, `/semester`, `/weekly`, `/topsubjects`, `/planfact`)
- Created `app/stats/service.py` containing all helper functions (normalization, exclusions, semester bounds, time utilities, duration calculations, filtering)
- Updated `app/main.py` to import and include the stats router: `from app.stats import router as stats_router` and `app.include_router(stats_router, prefix="/api/stats")`
- Removed duplicate stats endpoints and helper functions from `app/main.py`
- Created `app/stats/__init__.py` to make the module importable

## Changes

### Files Created
- `app/stats/routes.py` - Contains the FastAPI router with all stats endpoints
- `app/stats/service.py` - Contains all helper functions used by the stats endpoints
- `app/stats/__init__.py` - Makes stats a proper Python package

### Files Modified
- `app/main.py` - 
  - Added import: `from app.stats import router as stats_router`
  - Added router inclusion: `app.include_router(stats_router, prefix="/api/stats")`
  - Removed the original `/api/stats` endpoint (get_stats function)
  - Removed all duplicate stats endpoints: `/api/stats/semester`, `/api/stats/weekly`, `/api/stats/topsubjects`, `/api/stats/planfact`
  - Removed all duplicate helper functions: 
    * normalize_schedule_value
    * normalize_schedule_category
    * get_schedule_exclusions
    * lesson_is_visible
    * get_semester_bounds
    * _as_aware_utc
    * lesson_duration_hours
    * clipped_lesson_duration_hours
    * get_filtered_semester_lessons

## Verification

- Verified that the FastAPI application can be imported successfully (despite unrelated bcrypt warning)
- Confirmed via git diff that only the expected changes were made:
  * Added stats router import and inclusion in main.py
  * Removed duplicate endpoints and helper functions (~550 lines removed from main.py)
  * Added approximately 600 lines of code in the new stats module files
- The endpoints are now accessible at `/api/stats/*` with the same functionality as before

## Why

This change follows the target architecture outlined in `docs/architecture-target.md` where each feature area (like stats) has its own routes.py and service.py. It improves separation of concerns by moving HTTP route handling to routes.py and business logic to service.py.

## How to Apply

1. The changes are already applied in this commit
2. To run the application, use the usual method (uvicorn app.main:app)
3. The stats endpoints will be available at `/api/stats/*` requiring authentication
4. No further action needed - the refactoring is complete