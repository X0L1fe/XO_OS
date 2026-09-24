from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


class LlamaCppClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8080/v1", api_key: str = "no-key-needed"):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(base_url=self.base_url, api_key=self.api_key)

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
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def close(self):
        await self.client.aclose()


# Global client instance (to be initialized with settings)
llama_client: Optional[LlamaCppClient] = None


def get_llama_client() -> LlamaCppClient:
    global llama_client
    if llama_client is None:
        settings = Settings()
        llama_client = LlamaCppClient(
            base_url=getattr(settings, "LLAMA_CPP_BASE_URL", "http://127.0.0.1:8080/v1"),
            api_key=getattr(settings, "LLAMA_CPP_API_KEY", "no-key-needed"),
        )
    return llama_client