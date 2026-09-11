from __future__ import annotations

import json
import os

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional, List

from fastapi import (
    FastAPI,
    File,
    Query,
    UploadFile,
    HTTPException,
    Request,
    Body,
    Form, 
    Depends,
    Cookie, 
    Response, 
    status
)
from pydantic import BaseModel
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport.requests import Request as GoogleRequest

from app.database.db import Database
from app.config import Settings
from app.sync.service import SyncService
from app.mais_parser import fetch_groups, fetch_group_schedule, parse_mais_schedule
from app.database.models import UserStats, Lesson, User, Session
from app.auth.service import (
    get_password_hash,
    verify_password,
    create_user,
    authenticate_user,
    update_onboarding_completed,
    create_session,
    get_user_from_session,
    delete_session,
)
from app.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    AuthStatusResponse
    )

from app.telegram.service import (
    create_telegram_link_code,
    unlink_telegram_account,
)
from app.telegram.schemas import (
    TelegramLinkResponse,
    TelegramStatusResponse,
    TelegramUnlinkResponse,
)

# Try to import Google Calendar service; if not available, set to None.
try:
    from app.google_calendar.service import GoogleCalendarSyncService
    from app.google_calendar.auth import get_credentials_path, get_token_path, SCOPES
    from google_auth_oauthlib.flow import Flow
    GOOGLE_OAUTH_AVAILABLE = True
except ImportError:
    GoogleCalendarSyncService = None
    GOOGLE_OAUTH_AVAILABLE = False

app = FastAPI(title='XO_OS', version='0.1.0')

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:8000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

db = Database()

# Obsidian vault path configuration
OBSIDIAN_CONFIG_PATH = Path('data/obsidian_config.json')

def get_obsidian_vault_path() -> Optional[str]:
    if OBSIDIAN_CONFIG_PATH.is_file():
        try:
            data = json.loads(OBSIDIAN_CONFIG_PATH.read_text(encoding='utf-8'))
            return data.get('vault_path')
        except Exception:
            return None
    return None

def save_obsidian_vault_path(path: str) -> None:
    OBSIDIAN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {'vault_path': path}
    OBSIDIAN_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding='utf-8')

# Serve static files (frontend) if directory exists
frontend_dir = Path(__file__).parent / 'web'
if frontend_dir.is_dir():
    # We'll serve static files via a catch-all route below
    pass

# Dependency to get current user from session cookie
def get_current_user(session_token: Optional[str] = Cookie(None)) -> Optional[User]:
    if not session_token:
        return None
    with db.session() as db_session:
        return get_user_from_session(db_session, session_token)

# Dependency to require authentication
def get_current_active_user(current_user: Optional[User] = Depends(get_current_user)) -> User:
    if not current_user:
        raise HTTPException(status_code=401, detail='Not authenticated')
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user

# API routes under /api prefix
@app.get('/api/health')
def health() -> dict[str, str]:
    return {'status': 'ok', 'service': 'XO_OS'}


@app.post('/api/export')
async def export_to_obsidian(vault: Optional[str] = None, current_user: User = Depends(get_current_active_user)) -> dict[str, Any]:
    '''Export lessons to Obsidian vault.'''
    try:
        vault_path = vault or get_obsidian_vault_path() or os.getenv('OBSIDIAN_VAULT_PATH')
        if not vault_path:
            return {
                'status': 'error',
                'message': "Obsidian vault path not provided. Set OBSIDIAN_VAULT_PATH environment variable, save via /api/obsidian/path, or pass 'vault' parameter."
            }
        exported = SyncService(db).export_to_obsidian(vault_path)
        return {
            'status': 'success',
            'exported': exported,
            'message': f'Exported {exported} lessons to Obsidian vault at {vault_path}'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Failed to export to Obsidian: {str(e)}'
        }


@app.post('/api/auth/register')
async def register(user: UserCreate) -> Response:
    '''Register a new user.'''
    try:
        print(f"DEBUG: ENTERING TRY BLOCK")
        print(f"DEBUG: About to call create_user")
        with db.session() as db_session:
            db_user = create_user(db_session, user)
            db_session_obj = create_session(db_session, db_user.id)
            response = {
                'success': True,
                'user': UserResponse.model_validate(db_user).model_dump()
            }
            res = Response(
                content=json.dumps(response), 
                media_type='application/json'
                )
            res.set_cookie(
                key='session_token',
                value=db_session_obj.token,
                httponly=True,
                max_age=86400,  # 1 day
                samesite='lax',
                path='/',
            )
            return res

    except HTTPException:
        raise
    
    except Exception as e:
        # Log the exception for debugging
        print(f"Registration error: {e}")
        import traceback
        traceback.print_exc()

        res = Response(
            content=json.dumps({
            'detail': str(e),
            'type': type(e).__name__,
            }),
            media_type='application/json',
            status_code=500
            )
        return res


@app.post('/api/auth/login')
async def login(user: UserLogin) -> Response:
    '''Log in a user.'''
    with db.session() as db_session:
        db_user = authenticate_user(db_session, user.email, user.password)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверный email или пароль',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        # Create a session
        db_session_obj = create_session(db_session, db_user.id)
        response = {
            'success': True,
            'user': UserResponse.model_validate(db_user).model_dump()
        }
        res = Response(content=json.dumps(response), media_type='application/json')
        res.set_cookie(
            key='session_token',
            value=db_session_obj.token,
            httponly=True,
            max_age=86400,  # 1 day
            samesite='lax',
            path='/',
        )
        return res


@app.post('/api/auth/logout')
async def logout(session_token: Optional[str] = Cookie(None), current_user: Optional[User] = Depends(get_current_user)) -> dict[str, Any]:
    '''Log out the current user.'''
    with db.session() as db_session:
        if session_token:
            delete_session(db_session, session_token)
        # Clear the cookie
        from fastapi import Response
        res = Response(content=json.dumps({'success': True}), media_type='application/json')
        res.delete_cookie(key='session_token', path='/')
        return res


@app.get('/api/auth/me')
async def get_current_user_info(current_user: Optional[User] = Depends(get_current_user)) -> dict[str, Any]:
    '''Get the current user.'''
    if not current_user:
        return {
            'authenticated': False,
            'user': None
        }
    return {
        'authenticated': True,
        'user': UserResponse.model_validate(current_user)
    }


@app.get('/api/auth/status')
async def auth_status(current_user: Optional[User] = Depends(get_current_user)) -> AuthStatusResponse:
    '''Check authentication status.'''
    if not current_user:
        return AuthStatusResponse(
            authenticated=False,
            user=None,
            onboarding_completed=False
        )
    return AuthStatusResponse(
        authenticated=True,
        user=UserResponse.model_validate(current_user),
        onboarding_completed=current_user.onboarding_completed
    )


# Additional API routes
@app.get('/api/stats')
def get_stats(current_user: User = Depends(get_current_active_user)):
    '''Get stats for the current user.'''
    with db.session() as session:
        stats = session.query(UserStats).filter(UserStats.user_id == current_user.id).first()
        if not stats:
            # Should not happen if we create stats for each user, but just in case
            stats = UserStats(user_id=current_user.id)
            session.add(stats)
            session.commit()
        return {
            'level': stats.level,
            'total_xp': stats.total_xp,
            'current_streak': stats.current_streak,
            'max_streak': stats.max_streak,
            'last_activity_date': stats.last_activity_date.isoformat() if stats.last_activity_date else None
        }


@app.get('/api/now')
def get_now(current_user: User = Depends(get_current_active_user)):
    '''Get current lesson if any.'''
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    with db.session() as session:
        lesson = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time <= now,
            Lesson.end_time >= now
        ).order_by(Lesson.start_time).first()
        if lesson:
            return {
                'taskTitle': lesson.subject,
                'taskDesc': lesson.description or '',
                'timeEstimate': f'{lesson.start_time.strftime('%H:%M')} - {lesson.end_time.strftime('%H:%M')}',
                'priority': lesson.lesson_type,
                'xpReward': 10,  # XP per lesson as in sync service
                'time': lesson.start_time.strftime('%H:%M')
            }
        # No current lesson
        return {
            'taskTitle': '',
            'taskDesc': '',
            'timeEstimate': '',
            'priority': '',
            'xpReward': 0,
            'time': '--:--'
        }


@app.get('/api/schedule')
def get_schedule(current_user: User = Depends(get_current_active_user)):
    '''Get upcoming lessons.'''
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    with db.session() as session:
        lessons = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= now
        ).order_by(Lesson.start_time).limit(50).all()
        result = []
        for lesson in lessons:
            result.append({
                'time': lesson.start_time.strftime('%H:%M'),
                'subject': lesson.subject,
                'type': lesson.lesson_type,
                'room': lesson.room or '',
                'teacher': lesson.teacher or '',
                'status': 'sync' if lesson.google_event_id else 'unsynced'
            })
        return result


@app.get('/api/stats/semester')
def get_semester_stats(current_user: User = Depends(get_current_active_user)):
    '''Get semester stats.'''
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    # Determine semester boundaries: assuming spring semester Feb-May, autumn Sep-Dec
    if 2 <= now.month <= 5:
        # Spring semester: Feb 1 to May 31
        semester_start = datetime(now.year, 2, 1, tzinfo=timezone.utc)
        semester_end = datetime(now.year, 5, 31, 23, 59, 59, tzinfo=timezone.utc)
    elif 9 <= now.month <= 12:
        # Autumn semester: Sep 1 to Dec 31
        semester_start = datetime(now.year, 9, 1, tzinfo=timezone.utc)
        semester_end = datetime(now.year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    else:
        # Jan, Jun-Aug: no semester, return zeros
        return {'lecture': 0, 'practice': 0, 'lab': 0, 'total': 0}
    with db.session() as session:
        lectures = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= semester_start,
            Lesson.start_time <= semester_end,
            Lesson.lesson_type == 'LECTURE'
        ).count()
        practices = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= semester_start,
            Lesson.start_time <= semester_end,
            Lesson.lesson_type == 'PRACTICE'
        ).count()
        labs = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= semester_start,
            Lesson.start_time <= semester_end,
            Lesson.lesson_type == 'LAB'
        ).count()
        total = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= semester_start,
            Lesson.start_time <= semester_end
        ).count()
        return {
            'lecture': lectures,
            'practice': practices,
            'lab': labs,
            'total': total
        }


@app.get('/api/stats/weekly')
def get_weekly_stats(current_user: User = Depends(get_current_active_user)):
    '''Get weekly hours for the current week.'''
    from datetime import datetime, timezone, timedelta
    now = datetime.now(timezone.utc)
    # Start of week (Monday)
    start_of_week = now - timedelta(days=now.weekday())
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_week = start_of_week + timedelta(days=7)
    with db.session() as session:
        lessons = session.query(Lesson).filter(
            Lesson.user_id == current_user.id,
            Lesson.start_time >= start_of_week,
            Lesson.start_time < end_of_week
        ).all()
        total_hours = 0.0
        for lesson in lessons:
            duration = (lesson.end_time - lesson.start_time).total_seconds() / 3600.0
            total_hours += duration
        # Return as a single week (label '1')
        return [{'label': '1', 'hours': round(total_hours, 2)}]


@app.get('/api/stats/planfact')
def get_plan_fact(current_user: User = Depends(get_current_active_user)):
    '''Get plan vs fact hours.'''
    # Placeholder: plan/fact tracking not implemented.
    # Return zeros for all categories.
    return {
        'study': {'plan': 0, 'fact': 0},
        'projects': {'plan': 0, 'fact': 0},
        'self': {'plan': 0, 'fact': 0}
    }


@app.get('/api/stats/topsubjects')
def get_top_subjects(current_user: User = Depends(get_current_active_user)):
    '''Get top subjects by total hours.'''
    with db.session() as session:
        lessons = session.query(Lesson).filter(Lesson.user_id == current_user.id).all()
        subject_hours = {}
        for lesson in lessons:
            duration = (lesson.end_time - lesson.start_time).total_seconds() / 3600.0
            subject = lesson.subject
            subject_hours[subject] = subject_hours.get(subject, 0) + duration
        # Sort descending by hours and take top 5
        sorted_subjects = sorted(subject_hours.items(), key=lambda x: x[1], reverse=True)[:5]
        result = [{'name': subject, 'hours': round(hours, 2)} for subject, hours in sorted_subjects]
        return result


@app.get('/api/achievements')
def get_achievements(current_user: User = Depends(get_current_active_user)):
    '''Get achievements based on stats.'''
    with db.session() as session:
        stats = session.query(UserStats).filter(UserStats.user_id == current_user.id).first()
        if not stats:
            stats = UserStats(user_id=current_user.id)
            session.add(stats)
            session.commit()
        achievements = []
        # Streak achievements
        if stats.current_streak >= 7:
            achievements.append(f'Стаж {stats.current_streak} дней')
        if stats.current_streak >= 30:
            achievements.append(f'Стаж {stats.current_streak} дней')
        # Level achievements
        if stats.level >= 1:
            achievements.append(f'Уровень {stats.level}')
        if stats.level >= 5:
            achievements.append(f'Уровень {stats.level}')
        if stats.level >= 10:
            achievements.append(f'Уровень {stats.level}')
        # XP achievements
        if stats.total_xp >= 1000:
            achievements.append('Новичок')
        if stats.total_xp >= 5000:
            achievements.append('Опытный')
        if stats.total_xp >= 10000:
            achievements.append('Ветеран')
        return {
            'achievements': achievements,
            'streak': stats.current_streak
        }


@app.get('/api/calendar/status')
def get_calendar_status():
    '''Get calendar status.'''
    if not GOOGLE_OAUTH_AVAILABLE:
        return {'status': 'disconnected'}
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.valid:
                return {'status': 'connected'}
            elif creds and creds.expired and creds.refresh_token:
                # Try to refresh
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                return {'status': 'connected'}
        return {'status': 'disconnected'}
    except Exception:
        return {'status': 'disconnected'}


@app.get('/api/obsidian/status')
def get_obsidian_status():
    '''Get obsidian status.'''
    vault_path = os.getenv('OBSIDIAN_VAULT_PATH')
    if vault_path:
        return {'status': 'ready'}
    return {'status': 'not_configured'}


class ObsidianPath(BaseModel):
    vault: str

@app.get('/api/obsidian/path')
def get_obsidian_path():
    '''Get saved Obsidian vault path.'''
    path = get_obsidian_vault_path()
    if path is None:
        return {'path': ''}
    return {'path': path}


@app.post('/api/obsidian/path')
def set_obsidian_path(data: ObsidianPath):
    '''Save Obsidian vault path.'''
    vault = data.vault
    if not vault or not vault.strip():
        raise HTTPException(status_code=400, detail='Obsidian vault path cannot be empty')
    vault = vault.strip()
    save_obsidian_vault_path(vault)
    return {'status': 'success', 'path': vault}


@app.get('/api/mais/groups')
def get_mais_groups():
    '''Get list of MAIS groups.'''
    try:
        groups = fetch_groups()
        return {'groups': groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to fetch groups: {e}')


@app.post('/api/mais/import')
def import_mais_schedule(group_name: str = Form(...)):
    '''Import schedule for a given MAIS group name.'''
    try:
        # Fetch schedule JSON
        json_bytes = fetch_group_schedule(group_name)
        # Parse into LessonData
        lessons = parse_mais_schedule(json_bytes, group_name=group_name)
        # Import using SyncService
        sync_service = SyncService(db)
        result = sync_service.import_lesson_data(lessons)
        return {
            'status': 'success',
            'group': group_name,
            'parsed': result.parsed,
            'created': result.created,
            'updated': result.updated,
            'moved': result.moved,
            'deleted': result.deleted,
            'unchanged': result.unchanged,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to import schedule for group \'{group_name}\': {e}')


# Google OAuth endpoints
@app.get('/api/google/auth')
async def google_auth():
    '''Initiate Google OAuth2 flow.'''
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail='Google OAuth not available',
        )
    try:
        flow = Flow.from_client_secrets_file(
            get_credentials_path(),
            scopes=SCOPES,
            redirect_uri='http://localhost:8000/api/google/callback',
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
        )
        response = RedirectResponse(url=authorization_url)
        response.set_cookie(
            key='oauth_state',
            value=state,
            httponly=True,
            max_age=600,
            samesite='lax',
        )
        response.set_cookie(
            key='oauth_code_verifier',
            value=flow.code_verifier,
            httponly=True,
            max_age=600,
            samesite='lax',
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f'Failed to initiate OAuth flow: {e}',
        )


@app.get('/api/google/callback')
async def google_callback(request: Request):
    '''Handle Google OAuth2 callback.'''
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail='Google OAuth not available',
        )
    try:
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        saved_state = request.cookies.get('oauth_state')
        code_verifier = request.cookies.get('oauth_code_verifier')
        if not code:
            raise HTTPException(
                status_code=400,
                detail='Missing authorization code',
            )
        if not state or state != saved_state:
            raise HTTPException(
                status_code=400,
                detail='Invalid OAuth state',
            )
        if not code_verifier:
            raise HTTPException(
                status_code=400,
                detail='Missing PKCE code verifier',
            )
        flow = Flow.from_client_secrets_file(
            get_credentials_path(),
            scopes=SCOPES,
            redirect_uri='http://localhost:8000/api/google/callback',
            code_verifier=code_verifier,
            autogenerate_code_verifier=False,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        with open(
            get_token_path(),
            'w',
            encoding='utf-8',
        ) as token_file:
            token_file.write(creds.to_json())
        response = RedirectResponse(
            url='http://localhost:8000/#settings?connected=true'
        )
        response.delete_cookie('oauth_state')
        response.delete_cookie('oauth_code_verifier')
        return response
    except Exception as e:
        return RedirectResponse(
            url=(
                'http://localhost:8000/#settings'
                f'?error={str(e)}'
            )
        )


@app.get('/api/google/status')
async def google_status():
    '''Check Google connection status.'''
    if not GOOGLE_OAUTH_AVAILABLE:
        return {'connected': False, 'error': 'Google OAuth not available'}
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.valid:
                return {'connected': True}
            elif creds and creds.expired and creds.refresh_token:
                # Try to refresh
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                # Save refreshed token
                with open(token_path, 'w') as token_file:
                    token_file.write(creds.to_json())
                return {'connected': True}
        return {'connected': False}
    except Exception:
        return {'connected': False}


@app.post('/api/google/disconnect')
async def google_disconnect():
    '''Disconnect/revoke Google OAuth tokens.'''
    if not GOOGLE_OAUTH_AVAILABLE:
        raise HTTPException(status_code=501, detail='Google OAuth not available')
    try:
        token_path = get_token_path()
        if os.path.exists(token_path):
            os.remove(token_path)
        return {'success': True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to disconnect: {str(e)}')


@app.post('/api/debug/echo')
async def echo(request: Request):
    body = await request.body()
    try:
        decoded = body.decode('utf-8')
    except UnicodeDecodeError:
        decoded = body.decode('utf-8', errors='replace')
    return {'body': decoded, 'body_bytes': list(body)}


@app.get('/api/mais/import_get')
def import_mais_schedule_get(group_name: str):
    '''Get the group name as a test.'''
    return {'group_name': group_name}


# ============================================================
# TELEGRAM
# ============================================================

@app.post(
    "/api/telegram/link",
    response_model=TelegramLinkResponse,
)
async def telegram_link(
    current_user: User = Depends(get_current_active_user),
) -> TelegramLinkResponse:
    """
    Создаёт одноразовый код привязки учетной записи Telegram
    и создаёт Telegram deep link (/start CODE).
    """

    with db.session() as db_session:
        code, expires_at = create_telegram_link_code(
            db_session,
            current_user.id,
        )

    bot_username = Settings.telegram_bot_username.strip().lstrip("@")

    if not bot_username:
        raise HTTPException(
            status_code=500,
            detail="Telegram bot username is not configured",
        )

    deep_link = f"https://t.me/{bot_username}?start={code}"

    return TelegramLinkResponse(
        linked=False,
        code=code,
        expires_at=expires_at,
        deep_link=deep_link,
    )


@app.get(
    "/api/telegram/status",
    response_model=TelegramStatusResponse,
)
async def telegram_status(
    current_user: User = Depends(get_current_active_user),
) -> TelegramStatusResponse:
    """
    Return Telegram connection status.
    """

    return TelegramStatusResponse(
        linked=current_user.telegram_id is not None,
        telegram_id=current_user.telegram_id,
        linked_at=current_user.telegram_linked_at,
    )


@app.post(
    "/api/telegram/unlink",
    response_model=TelegramUnlinkResponse,
)
async def telegram_unlink(
    current_user: User = Depends(get_current_active_user),
) -> TelegramUnlinkResponse:
    """
    Unlink Telegram account.
    """

    with db.session() as db_session:
        unlink_telegram_account(
            db_session,
            current_user.id,
        )

    return TelegramUnlinkResponse(
        success=True,
    )

# Trigger reload

# Catch-all route for serving frontend (if exists)
@app.get('/{full_path:path}')
async def serve_frontend(full_path: str):
    '''Serve frontend.'''
    if frontend_dir.is_dir():
        requested_file = frontend_dir / full_path
        if requested_file.is_file():
            return FileResponse(requested_file)
        index_file = frontend_dir / 'index.html'
        if index_file.is_file():
            return FileResponse(index_file)
    raise HTTPException(status_code=404, detail='Frontend not found')
