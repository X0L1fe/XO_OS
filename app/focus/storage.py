"""
Хранилище файлов evidence.

Отвечает только за файловую систему: сохранение, удаление, лимиты.
Ничего не знает ни про БД, ни про FastAPI.
"""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger(__name__)

# app/focus/storage.py -> parents[1] = app/ -> app/web/static/media
MEDIA_ROOT: Path = Path(__file__).resolve().parents[1] / "web" / "static" / "media"

EVIDENCE_SUBDIR = "focus"

ALLOWED_IMAGE_MIME: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_IMAGE_BYTES: int = 5 * 1024 * 1024  # 5 MB


def save_evidence_image(
    user_id: int,
    raw_bytes: bytes,
    filename: str,
    content_type: str,
) -> str:
    """
    Сохраняет изображение evidence на диск.

    Возвращает путь относительно MEDIA_ROOT, например:
        "focus/42/9f2c...e1.jpg"
    """
    if content_type not in ALLOWED_IMAGE_MIME:
        raise ValueError(
            f"Unsupported image MIME type: {content_type}. "
            f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_MIME))}"
        )

    if not raw_bytes:
        raise ValueError("Image file is empty")

    if len(raw_bytes) > MAX_IMAGE_BYTES:
        raise ValueError(
            f"Image file is too large (max {MAX_IMAGE_BYTES // (1024 * 1024)} MB)"
        )

    ext = ALLOWED_IMAGE_MIME[content_type]
    rel_dir = Path(EVIDENCE_SUBDIR) / str(user_id)
    abs_dir = MEDIA_ROOT / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"{uuid4().hex}{ext}"
    abs_path = abs_dir / file_name
    abs_path.write_bytes(raw_bytes)

    rel_path = rel_dir / file_name
    # Всегда храним с прямыми слэшами, независимо от ОС
    return str(rel_path).replace("\\", "/")


def delete_evidence_image(rel_path: str) -> None:
    """
    Удаляет файл evidence, если он существует.
    Ошибки игнорируются (файл может быть уже удалён).
    """
    try:
        abs_path = MEDIA_ROOT / rel_path
        if abs_path.is_file():
            abs_path.unlink()
    except Exception:
        logger.exception("Failed to delete evidence file: %s", rel_path)
