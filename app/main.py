from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth.routes import router as auth_router
from app.calendar.routes import router as calendar_router
from app.common.health import router as health_router
from app.config import Settings
from app.database.db import Database
from app.debug.routes import router as debug_router
from app.events.routes import router as events_router
from app.focus import router as focus_router
from app.gamification import router as gamification_router
from app.google_calendar.routes import router as google_calendar_router
from app.mais.background import periodic_mais_check
from app.mais.routes import router as mais_router
from app.notifications.routes import router as notifications_router
from app.obsidian.routes import router as obsidian_router
from app.onboarding.routes import router as onboarding_router
from app.schedule import router as schedule_router
from app.stats import router as stats_router
from app.telegram.routes import router as telegram_router

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

# Не засоряем вывод INFO-логами сторонних библиотек
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = FastAPI(title="XO_OS", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://192.168.1.2:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

db = Database()
settings = Settings()

# Server-Sent Events for real-time updates
# We'll use a simple in-memory dictionary to track active connections
# In a production app, you would use a proper message queue like Redis Pub/Sub

app.include_router(stats_router, prefix="/api")
app.include_router(gamification_router, prefix="/api/gamification")
app.include_router(focus_router, prefix="/api")
app.include_router(schedule_router, prefix="/api/schedule")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(google_calendar_router, prefix="/api")
app.include_router(telegram_router, prefix="/api")
app.include_router(obsidian_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(onboarding_router, prefix="/api")
app.include_router(debug_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(mais_router, prefix="/api")

# Serve static files (frontend) if directory exists
frontend_dir = Path(__file__).parent / "web"
if frontend_dir.is_dir():
    # We'll serve static files via a catch-all route below
    pass


# Startup event to launch the background task
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(periodic_mais_check())


# Catch-all route for serving frontend (if exists)
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    # Не перехватываем API-пути
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404, detail="Not Found")

    # Если запрошен реальный файл — отдаём его
    file_path = frontend_dir / full_path
    if file_path.is_file():
        return FileResponse(file_path)

    # Иначе — SPA-роут
    return FileResponse(frontend_dir / "index.html")
