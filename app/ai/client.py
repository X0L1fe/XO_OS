from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

# Какие статусы считаем временными и повторяем
_RETRYABLE_STATUSES = {502, 503, 504}
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0  # секунды


class LlamaCppClient:
    def __init__(
        self,
        base_url: str = "http://192.168.1.2:8080/v1",
        api_key: str = "no-key-needed",
    ):
        self.base_url = base_url
        self.api_key = api_key

        headers = {"Content-Type": "application/json"}
        # llama.cpp обычно не требует ключ, но если требуется — шлём Bearer
        if api_key and api_key != "no-key-needed":
            headers["Authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=httpx.Timeout(60.0, connect=10.0),
        )

    async def chat_completion(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        top_p: float = 0.9,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the llama.cpp server.

        Повторяет запрос при временных 5xx-ошибках (502/503/504) с
        экспоненциальной паузой.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }

        last_exc: Exception | None = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = await self.client.post("/chat/completions", json=payload)
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                body = (e.response.text or "")[:500]
                last_exc = e

                if status_code in _RETRYABLE_STATUSES and attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "llama.cpp returned %s (attempt %d/%d), "
                        "retrying in %.1fs. Body: %s",
                        status_code,
                        attempt + 1,
                        _MAX_RETRIES,
                        delay,
                        body,
                    )
                    await asyncio.sleep(delay)
                    continue

                logger.error(
                    "llama.cpp HTTP error %s: %s",
                    status_code,
                    body,
                )
                raise

            except httpx.RequestError as e:
                last_exc = e
                if attempt < _MAX_RETRIES - 1:
                    delay = _RETRY_BASE_DELAY * (2**attempt)
                    logger.warning(
                        "llama.cpp request error (attempt %d/%d): %s. "
                        "Retrying in %.1fs",
                        attempt + 1,
                        _MAX_RETRIES,
                        e,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    continue
                logger.error("llama.cpp request error: %s", e)
                raise

        # На всякий случай — если цикл выпал без return/raise
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("chat_completion failed without exception")


# Global client instance (to be initialized with settings)
llama_client: Optional[LlamaCppClient] = None


def get_llama_client() -> LlamaCppClient:
    global llama_client
    if llama_client is None:
        settings = Settings()
        llama_client = LlamaCppClient(
            base_url=getattr(
                settings, "LLAMA_CPP_BASE_URL", "http://192.168.1.2:8080/v1"
            ),
            api_key=getattr(settings, "LLAMA_CPP_API_KEY", "no-key-needed"),
        )

    return llama_client
