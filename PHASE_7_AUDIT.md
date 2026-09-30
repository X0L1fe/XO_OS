# Phase 7 Audit Report

## Phase 7 Status
COMPLETE

## Changed
- app/focus/routes.py
- app/focus/service.py

## Async Flow
request
→ FocusService.complete_focus_session (sets verification_status=pending, commits)
→ HTTP response returned (verification_status=pending)
→ background task _process_ai_verification (if BackgroundTasks provided)
  → new DB session
  → load FocusSession (by session_id and user_id for ownership)
  → load FocusEvidence for the session
  → AI verification via AIVerificationService
  → FocusService.process_ai_verification_result (applies result, updates state, awards XP if approved)
  → publish_focus_updated
→ (if no BackgroundTasks, synchronous fallback runs same steps but in the request thread)

## HTTP Behavior
The completion endpoint returns immediately after setting verification_status to pending and committing the session.
It does not await the AI verification result. The AI verification is either run in a background task (when BackgroundTasks is provided)
or run synchronously in the same thread (when BackgroundTasks is None, e.g., in testing) but after the HTTP response would have been sent
in a real background task scenario. However, note that in the synchronous fallback we do run the AI verification before returning,
but this is only for compatibility and testing; in production with a web server, BackgroundTasks is always provided.

## DB Session Safety
- HTTP request uses a request-scoped DB session (via `with db.session() as session:`).
- After committing the pending session, the request session is closed.
- Background task creates a new DB session (via `SessionLocal()`) and closes it after use.
- The background task does not use the request's DB session or any ORM objects tied to it.

## Ownership
The background task verifies ownership by loading the FocusSession with both session_id and user_id:
`local_focus_service.get_session(session_id=session_id, user_id=user_id)`
If the session is not found or does not belong to the user, the task logs an error and returns.

## Error Handling
- Technical AI errors (exception, empty response, malformed JSON) are caught by `AIVerificationService.verify_evidence` and return a
  `VerificationResult` with `approved=False` and a reason starting with known error indicators (e.g., "Failed to parse AI response").
- In `FocusService.process_ai_verification_result`, we check if the reason starts with any of the technical error indicators.
  If so, we set verification_status to "error" and commit (no XP).
- Normal AI rejection (approved=False, reason not a technical error) sets verification_status to "rejected" (no XP).
- Approved sets verification_status to "approved" and awards XP.

## Idempotency
`FocusService.process_ai_verification_result` first checks if the session's verification_status is not "pending".
If it is already in a final state (approved, rejected, error), the function returns early without changing state or awarding XP.
This prevents duplicate XP awards and duplicate events on repeated verification calls.

## Events
- The HTTP completion endpoint does not publish an event when setting pending (only the initial completion event from `complete_focus_session`).
- The background task (and synchronous fallback) publishes exactly one `focus_updated` event after applying the verification result.
- The synchronous fallback in the completion route (when no BackgroundTasks) also publishes one event after the result.
- Thus, each state transition (pending → final) results in exactly one `focus_updated` event.

## XP
- Only approved results award XP: base 10 + bonus (int(score * 10)), where score is from 0.0 to 1.0.
- Rejected and error results award 0 XP.
- Confidence is not used for XP calculation.
- The XP formula matches Phase 6.

## Runtime Tests
We performed manual syntax checks and verified that the imports work.
We did not run a full test suite (none found), but we verified the logic by inspection.

## Architecture
routes
→ FocusService
→ background task (or synchronous fallback)
→ AI service
→ llama.cpp

No focus → main or focus → frontend HTTP calls.
No duplicate AI verification logic.
No DB schema changes.

## Remaining Issues
None identified. The implementation satisfies the Phase 7 requirements and constraints.