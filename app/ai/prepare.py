"""
Подготовка evidence к отправке в Qwen2.5-VL.

Отвечает за:
  - обрезку текстовых доказательств;
  - загрузку URL и извлечение чистого текста;
  - чтение, ресайз и base64-кодирование изображений.

Ничего не знает про БД, FastAPI и сам llama.cpp.
"""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from PIL import Image

logger = logging.getLogger(__name__)

# app/ai/prepare.py -> parents[1] = app/ -> app/web/static/media
MEDIA_ROOT: Path = Path(__file__).resolve().parents[1] / "web" / "static" / "media"

# --- Лимиты (подобраны под n_ctx=4096 и Qwen2.5-VL) ---
MAX_TEXT_EVIDENCE_CHARS = 3000  # на одно текстовое доказательство
MAX_URL_TEXT_CHARS = 2500  # на одну страницу
MAX_URL_FETCH_BYTES = 500_000  # 500 KB HTML максимум
MAX_IMAGE_DIMENSION = 512  # длинная сторона после ресайза
IMAGE_JPEG_QUALITY = 80

URL_FETCH_TIMEOUT = 15.0
URL_FETCH_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; MAISync/1.0; +https://example.local)"
}


def truncate_text(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + " …[truncated]"


async def fetch_url_text(url: str) -> Optional[str]:
    """
    Загружает страницу по URL и возвращает очищенный текст.

    Возвращает None, если страницу не удалось получить или распарсить.
    """
    try:
        async with httpx.AsyncClient(
            timeout=URL_FETCH_TIMEOUT,
            headers=URL_FETCH_HEADERS,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            html = response.text[:MAX_URL_FETCH_BYTES]
    except Exception as e:
        logger.warning("Failed to fetch URL %s: %s", url, e)
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(
            ["script", "style", "noscript", "header", "footer", "nav", "svg"]
        ):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
    except Exception as e:
        logger.warning("Failed to parse HTML from %s: %s", url, e)
        return None

    return truncate_text(text, MAX_URL_TEXT_CHARS)


def load_image_as_data_url(rel_path: str) -> Optional[str]:
    """
    Читает картинку из MEDIA_ROOT/<rel_path>, ресайзит и возвращает
    data:image/jpeg;base64,... для OpenAI-compatible content.
    """
    if not rel_path:
        return None

    abs_path = MEDIA_ROOT / rel_path
    if not abs_path.is_file():
        logger.warning("Image evidence not found: %s", rel_path)
        return None

    try:
        with Image.open(abs_path) as img:
            img = img.convert("RGB")

            # Уменьшаем, если больше лимита, сохраняя пропорции
            if max(img.size) > MAX_IMAGE_DIMENSION:
                img.thumbnail(
                    (MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION),
                    Image.LANCZOS,
                )

            buffer = io.BytesIO()
            img.save(
                buffer,
                format="JPEG",
                quality=IMAGE_JPEG_QUALITY,
                optimize=True,
            )
            raw = buffer.getvalue()
    except Exception as e:
        logger.warning("Failed to process image %s: %s", rel_path, e)
        return None

    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/jpeg;base64,{b64}"
