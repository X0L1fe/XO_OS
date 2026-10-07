from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.auth.service import get_current_active_user
from app.config import Settings
from app.database.db import Database
from app.database.models import User
from app.sync.service import SyncService

# Obsidian vault path configuration
OBSIDIAN_CONFIG_PATH = Path("data/obsidian_config.json")


def get_obsidian_vault_path() -> Optional[str]:
    if OBSIDIAN_CONFIG_PATH.is_file():
        try:
            data = json.loads(OBSIDIAN_CONFIG_PATH.read_text(encoding="utf-8"))
            return data.get("vault_path")
        except Exception:
            return None
    return None


def save_obsidian_vault_path(path: str) -> None:
    OBSIDIAN_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"vault_path": path}
    OBSIDIAN_CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


class ObsidianPath(BaseModel):
    vault: str


router = APIRouter()


@router.post("/export")
async def export_to_obsidian(
    vault: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Экспортируйте занятия в Obsidian.
    """
    try:
        vault_path = (
            vault or get_obsidian_vault_path() or os.getenv("OBSIDIAN_VAULT_PATH")
        )
        if not vault_path:
            return {
                "status": "error",
                "message": "Obsidian vault path not provided. Set OBSIDIAN_VAULT_PATH environment variable, save via /api/obsidian/path, or pass 'vault' parameter.",
            }
        # Import Database and db instance from main module
        from app.main import db

        exported = SyncService(db).export_to_obsidian(vault_path)
        return {
            "status": "success",
            "exported": exported,
            "message": f"Exported {exported} lessons to Obsidian vault at {vault_path}",
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to export to Obsidian: {str(e)}"}


@router.get("/obsidian/status")
def get_obsidian_status():
    """Get obsidian status."""
    vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if vault_path:
        return {"status": "ready"}
    return {"status": "not_configured"}


@router.get("/obsidian/path")
def get_obsidian_path():
    """Get saved Obsidian vault path."""
    path = get_obsidian_vault_path()
    if path is None:
        return {"path": ""}
    return {"path": path}


@router.post("/obsidian/path")
def set_obsidian_path(data: ObsidianPath):
    """Save Obsidian vault path."""
    vault = data.vault
    if not vault or not vault.strip():
        raise HTTPException(
            status_code=400, detail="Obsidian vault path cannot be empty"
        )
    vault = vault.strip()
    save_obsidian_vault_path(vault)
    return {"status": "success", "path": vault}
