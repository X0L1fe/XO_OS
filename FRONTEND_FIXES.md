# Frontend Fixes for XO_OS

## Changes Made

### Header.js (`xo-os-web/src/components/Header.js`)
- Added React state for user data, sync status, last check, and online status.
- Implemented `useEffect` to fetch user data from `/api/auth/me` on mount.
- Implemented periodic polling (every 30s) for sync status (`/api/google/status`) and online status (`/api/health`).
- Replaced static "Пользователь" with dynamic `{user.name}`.
- Replaced static "Синхронизировано" with dynamic `{syncStatus}`.
- Replaced static "Онлайн" with dynamic `{online ? 'Онлайн' : 'Офлайн'}`.
- Added logout button (`AiOutlineLogout`) that calls `/api/auth/logout` (POST) and clears user state.
- If user not authenticated, header returns null (could be adjusted to show guest state).

### Sidebar.js (`xo-os-web/src/components/Sidebar.js`)
- Added React state for sync status, last sync time, online status, and version.
- Implemented `useEffect` to fetch sync status from `/api/google/status`, online status from `/api/health`, and stats from `/api/stats` on mount and every 30s.
- Replaced static "Синхронизировано" with dynamic `{syncStatus}`.
- Replaced static "Сегодня, 14:32" with dynamic `{lastSync}`.
- Replaced static version text with dynamic `{version}`.
- Added online status indicator showing `{online ? 'Онлайн' : 'Офлайн'}`.
- Kept existing navigation and collapsed sidebar logic intact.

## How It Works
- Upon loading the frontend, Header and Sidebar components mount and start fetching data from the backend.
- User information (name) is retrieved from `/api/auth/me` (requires session cookie).
- Google Calendar sync status is retrieved from `/api/google/status`.
- Online/offline status is determined by availability of `/api/health` endpoint.
- Data is refreshed every 30 seconds to reflect changes.
- Logout endpoint clears the session cookie on the backend and removes user state on the frontend.

## Notes
- Ensure the backend is running and accessible from the frontend (same origin or CORS configured).
- The frontend dev server may need to be restarted to pick up the changes.
- If authentication fails, the header will not display (returns null). Consider showing a login prompt or guest state if desired.
- For more accurate "last sync" time, consider extending `/api/stats` or `/api/auth/me` to include `last_activity_date` from UserStats; currently we use a placeholder timestamp.

These changes make the UI reflect real user data, sync status, and provide a functional logout button.