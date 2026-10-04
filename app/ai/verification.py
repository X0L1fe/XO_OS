# app/ai/verification.py
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from app.ai.client import LlamaCppClient, get_llama_client
from app.ai.prepare import (
    MAX_TEXT_EVIDENCE_CHARS,
    fetch_url_text,
    load_image_as_data_url,
    truncate_text,
)

logger = logging.getLogger(__name__)

MODEL_NAME = "Qwen2.5-VL-7B-Instruct-Q4_K_M"
MAX_EVIDENCE_COUNT = 5
MAX_GOAL_CHARS = 400


class VerificationResult:
    def __init__(
        self,
        approved: bool,
        confidence: float,
        score: float,
        reason: str,
        missing: list[str],
    ):
        self.approved = approved
        self.confidence = confidence
        self.score = score
        self.reason = reason
        self.missing = missing

    def to_dict(self) -> Dict[str, Any]:
        return {
            "approved": self.approved,
            "confidence": self.confidence,
            "score": self.score,
            "reason": self.reason,
            "missing": self.missing,
        }


class AIVerificationService:
    def __init__(self, llama_client: Optional[LlamaCppClient] = None):
        self.llama_client = llama_client or get_llama_client()

    # ------------------------------------------------------------------
    # Подготовка evidence
    # ------------------------------------------------------------------

    async def _prepare_blocks(self, evidence_list: list[dict]) -> list[dict]:
        """
        Превращает сырые dicts из БД в готовые к отправке блоки:
          {"type": "text",  "content": "..."}
          {"type": "url",   "url": "...", "content": "..."}
          {"type": "image", "data_url": "data:image/jpeg;base64,..."}
          {"type": "image_missing"} — файл не найден/не обработан
        """
        prepared: list[dict] = []

        for ev in evidence_list[:MAX_EVIDENCE_COUNT]:
            ev_type = (ev.get("type") or "").lower()

            if ev_type == "text":
                content = truncate_text(ev.get("content", ""), MAX_TEXT_EVIDENCE_CHARS)
                prepared.append({"type": "text", "content": content})

            elif ev_type == "url":
                url = (ev.get("content") or "").strip()
                page_text = await fetch_url_text(url) if url else None
                prepared.append(
                    {
                        "type": "url",
                        "url": url,
                        "content": page_text
                        or "(не удалось загрузить содержимое страницы)",
                    }
                )

            elif ev_type == "image":
                data_url = load_image_as_data_url(ev.get("file_path") or "")
                if data_url:
                    prepared.append({"type": "image", "data_url": data_url})
                else:
                    prepared.append({"type": "image_missing"})

            else:
                logger.warning("Unknown evidence type in verification: %r", ev_type)

        return prepared

    # ------------------------------------------------------------------
    # Сборка сообщений для Qwen
    # ------------------------------------------------------------------

    def _build_messages(
        self,
        goal: str,
        prepared_blocks: list[dict],
    ) -> list[dict]:
        text_parts: list[str] = []
        image_data_urls: list[str] = []

        text_parts.append(
            "You verify whether the provided evidence proves completion of a goal."
        )
        text_parts.append("")
        text_parts.append("Goal:")
        text_parts.append(truncate_text(goal, MAX_GOAL_CHARS))
        text_parts.append("")
        text_parts.append("Evidence:")

        if not prepared_blocks:
            text_parts.append("(no evidence provided)")
        else:
            for i, block in enumerate(prepared_blocks, 1):
                btype = block["type"]
                if btype == "text":
                    text_parts.append(f"--- Evidence {i} [text] ---")
                    text_parts.append(block["content"])
                elif btype == "url":
                    text_parts.append(f"--- Evidence {i} [url] ---")
                    text_parts.append(f"URL: {block['url']}")
                    text_parts.append("Page content:")
                    text_parts.append(block["content"])
                elif btype == "image":
                    text_parts.append(
                        f"--- Evidence {i} [image] --- see attached image below."
                    )
                    image_data_urls.append(block["data_url"])
                elif btype == "image_missing":
                    text_parts.append(
                        f"--- Evidence {i} [image] --- "
                        f"file unavailable, treat as missing."
                    )
                text_parts.append("")

        text_parts.append(self._json_instructions())

        prompt_text = "\n".join(text_parts).strip()

        # Если картинок нет — отдаём строку (чуть проще для сервера),
        # если есть — собираем multimodal content-массив.
        if not image_data_urls:
            content: Any = prompt_text
        else:
            content = [{"type": "text", "text": prompt_text}]
            for data_url in image_data_urls:
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": data_url},
                    }
                )

        return [{"role": "user", "content": content}]

    @staticmethod
    def _json_instructions() -> str:
        return (
            "Return ONLY a single valid JSON object with no markdown fences "
            "and no extra text.\n"
            "Schema:\n"
            "{\n"
            '  "approved": true | false,\n'
            '  "confidence": 0.0,\n'
            '  "score": 0.0,\n'
            '  "reason": "short explanation",\n'
            '  "missing": ["..."]\n'
            "}\n"
            "Rules:\n"
            "- approved=true only when the evidence sufficiently proves the goal.\n"
            "- score and confidence are floats between 0.0 and 1.0.\n"
            "- missing is an array of concrete missing requirements ([] if none).\n"
            "- Text evidence may be unreliable; do not reward unsupported claims.\n"
            "- For URLs, judge only by the provided page content.\n"
            "- For images, judge visually."
        )

    # ------------------------------------------------------------------
    # Парсинг ответа
    # ------------------------------------------------------------------

    def _parse_response(self, response_text: str) -> VerificationResult:
        json_str = self._extract_json(response_text)
        if json_str is None:
            logger.error("No JSON object found in AI response: %s", response_text)
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason="No JSON found in AI response",
                missing=["No JSON in response"],
            )

        try:
            data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse AI response as JSON: %s", e)
            logger.error("Response text: %s", response_text)
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason="Failed to parse AI response",
                missing=["AI response parsing error"],
            )

        try:
            approved = bool(data.get("approved", False))
            confidence = self._clamp01(data.get("confidence", 0.0))
            score = self._clamp01(data.get("score", 0.0))
            reason = str(data.get("reason", "")).strip()
            missing = data.get("missing", [])
            if not isinstance(missing, list):
                missing = []
            missing = [str(x) for x in missing]
        except (TypeError, ValueError) as e:
            logger.error("Invalid field types in AI response: %s", e)
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason="Invalid AI response fields",
                missing=["Invalid AI response fields"],
            )

        return VerificationResult(
            approved=approved,
            confidence=confidence,
            score=score,
            reason=reason,
            missing=missing,
        )

    @staticmethod
    def _extract_json(text: str) -> Optional[str]:
        if not text:
            return None

        # Убираем markdown-обёртку ```json ... ```
        cleaned = re.sub(r"^\s*```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)

        # Ищем первый сбалансированный { ... }
        start = cleaned.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return cleaned[start : i + 1]
        return None

    @staticmethod
    def _clamp01(value: Any) -> float:
        try:
            v = float(value)
        except (TypeError, ValueError):
            return 0.0
        return min(1.0, max(0.0, v))

    # ------------------------------------------------------------------
    # Публичный API
    # ------------------------------------------------------------------

    async def verify_evidence(
        self, goal: str, evidence_list: list[dict]
    ) -> VerificationResult:
        if not goal or not evidence_list:
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason="Goal or evidence is missing",
                missing=["Goal or evidence missing"],
            )

        prepared_blocks = await self._prepare_blocks(evidence_list)
        messages = self._build_messages(goal, prepared_blocks)

        # Грубая оценка размера текста для лога
        text_len = 0
        image_count = 0
        for part in (
            messages[0]["content"] if isinstance(messages[0]["content"], list) else []
        ):
            if part.get("type") == "text":
                text_len += len(part.get("text", ""))
            elif part.get("type") == "image_url":
                image_count += 1
        if isinstance(messages[0]["content"], str):
            text_len = len(messages[0]["content"])

        logger.info(
            "AI verification: goal_len=%d evidence_count=%d "
            "prepared_blocks=%d image_blocks=%d prompt_chars=%d approx_prompt_tokens=%d",
            len(goal),
            len(evidence_list),
            len(prepared_blocks),
            image_count,
            text_len,
            text_len // 4,
        )

        try:
            response = await self.llama_client.chat_completion(
                model=MODEL_NAME,
                messages=messages,
                temperature=0.2,
                max_tokens=512,
                top_p=0.9,
                stream=False,
            )
        except Exception as e:
            logger.error("Error during AI verification: %s", e)
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason=f"AI verification error: {str(e)}",
                missing=["AI verification exception"],
            )

        response_text = (
            response.get("choices", [{}])[0].get("message", {}).get("content", "")
        )
        if not response_text:
            logger.error("Empty response from AI")
            return VerificationResult(
                approved=False,
                confidence=0.0,
                score=0.0,
                reason="Empty response from AI",
                missing=["Empty AI response"],
            )

        return self._parse_response(response_text)


# Global service instance
ai_verification_service: Optional[AIVerificationService] = None


def get_ai_verification_service() -> AIVerificationService:
    global ai_verification_service
    if ai_verification_service is None:
        ai_verification_service = AIVerificationService()
    return ai_verification_service
