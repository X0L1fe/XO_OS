# Phase 8 Audit Report

## Current XP Sources

1. Manual completion: awarded in `FocusService.complete_focus_session` when `completion_mode == "manual"`.
   - Amount: 3 XP (hardcoded)
   - Reason: "focus_completed"
   - Source type: focus_session
   - Source ID: session.id

2. AI verified completion: awarded in `FocusService.process_ai_verification_result` when `verification_result.approved == True`.
   - Amount: base_xp = 10 + bonus_xp = int(verification_result.score * 10) (total 10-20 XP)
   - Reason: "focus_verified"
   - Source type: focus_session
   - Source ID: session.id

3. No other XP awards found in the codebase (checked via grep for "_award_xp" and "XPTransaction").

## Current XP Formula

- Manual: fixed 3 XP
- AI approved: 10 + int(score * 10) XP, where score is a float between 0.0 and 1.0 from the AI verification result.
- Confidence is not used in XP calculation.

## Current XPTransaction Usage

- Created in `FocusService._award_xp` method.
- Fields: user_id, amount, reason, source_type="focus_session", source_id=session.id, created_at.
- Used as an audit trail of XP awards.

## Current Level Usage

- In `FocusService._award_xp`, after updating `stats.total_xp`, level is calculated as:
    new_level = (stats.total_xp // 1000) + 1
- If new_level > stats.level, then stats.level is updated.

## Current Streak Usage

- In `FocusService._award_xp`, streak is updated based on the last activity date:
    - If today is same as last_activity_date: streak unchanged.
    - If today is exactly one day after last_activity_date: increment streak.
    - Otherwise: reset streak to 1.
- Max streak is updated if current streak exceeds it.

## Current Gamification Events

- After updating UserStats and committing, `FocusService._award_xp` calls `publish_gamification_updated(user_id)`.
- This event is used to notify the frontend of gamification changes.

## Current Focus Reward Flow

### Manual completion:
1. `complete_focus_session` (in FocusService) is called with completion_mode="manual".
2. Sets session.ended_at, calculates duration, etc.
3. Sets completion_mode to "manual".
4. Sets verification_status to "not_required".
5. Awards 3 XP via `_award_xp` (reason: "focus_completed").
6. Commits the session and returns.

### AI verified completion:
1. `complete_focus_session` (in FocusService) is called with completion_mode="ai_verified".
2. Sets session.ended_at, calculates duration, etc.
3. Sets completion_mode to "ai_verified".
4. Sets verification_status to "pending".
5. Does NOT award XP yet.
6. Commits the session and returns session with verification_status=pending.
7. The API route (in focus/routes.py) then either:
   a. If BackgroundTasks is provided: adds a background task `_process_ai_verification` that will:
        - Create a new DB session.
        - Retrieve the session by session_id and user_id (ownership check).
        - Retrieve evidence for the session.
        - Call AI verification service.
        - Call `FocusService.process_ai_verification_result` with the result.
        - In `process_ai_verification_result`:
            - If approved: set verification_status to "approved", award XP (10 + bonus) via `_award_xp` (reason: "focus_verified").
            - If rejected: set verification_status to "rejected", no XP.
            - If technical error: set verification_status to "error", no XP.
        - Publishes focus_updated event.
   b. If BackgroundTasks is None (synchronous fallback): runs the AI verification synchronously and then calls `process_ai_verification_result` and awards XP if approved.

## Note on Duration

- The FocusSession model includes a `duration_seconds` field that is set in `complete_focus_session`.
- However, this duration is not used in XP calculation for either manual or AI verified completion.
- Duration is only stored for record-keeping and possibly for display.

## Note on Sync/Import

- XP awards WERE found in the sync modules (app/sync/service.py) in the `_update_stats` method.
- Lines 376-378: `xp_earned = lessons_imported * 10` and `stats.total_xp += xp_earned`
- This violated the Phase 8 requirement that XP should not be awarded for sync/import activities.
- FIXED: Removed the XP awarding while preserving other stats updates (streak, last activity date).
- Note: Level calculation is still based on total_xp, but since we no longer add XP for sync/import, level will only increase from focus session completions.

## Note on Idempotency

- `FocusService.process_ai_verification_result` includes an idempotency check: if the session's verification_status is not "pending", it returns early without changing state or awarding XP.
- This prevents duplicate XP awards if the verification result is processed multiple times.

## Database Schema

- No changes to DB schema have been made in Phase 6 or 7.
- The FocusSession model includes:
    - xp_awarded (Integer, default=0)
    - verification_status (String, default="not_required")
    - completion_mode (String, nullable)
- The XPTransaction model exists as an audit trail.

## Remaining Issues

- Need to verify that sync/import activities do not award XP.
- Need to ensure that the XP awarding logic is centralized and only occurs via `_award_xp`.
- Need to confirm that the current XP amounts match the desired model (manual: 3 XP, AI approved: 10-20 XP).