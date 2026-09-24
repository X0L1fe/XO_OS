from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, Optional

from app.ai.client import LlamaCppClient, get_llama_client

logger = logging.getLogger(__name__)


class VerificationResult:
    def __init__(self, approved: bool, confidence: float, score: float, reason: str, missing: list[str]):
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

    def _build_prompt(self, goal: str, evidence_list: list[dict]) -> str:
        """
        Build a prompt for the AI to verify evidence against the goal.
        We ask for a JSON response with specific fields.
        """
        # Format evidence for the prompt
        evidence_text = ""
        for i, ev in enumerate(evidence_list, 1):
            ev_type = ev.get("type", "unknown")
            ev_content = ev.get("content", "")
            if ev_type == "text":
                evidence_text += f"Evidence {i} (text): {ev_content}\n"
            elif ev_type == "url":
                evidence_text += f"Evidence {i} (url): {ev_content}\n"
            elif ev_type == "image":
                # Note: We are not actually sending the image, but we assume the content is a description or placeholder.
                # In a real implementation, we might need to encode the image and send it as a multimodal input.
                # However, the user said to use the existing llama.cpp server with the image projector.
                # We are going to assume that the content is a base64 string or a path? But the user said not to send raw bytes.
                # We'll just treat it as a description for now.
                evidence_text += f"Evidence {i} (image): {ev_content}\n"
            elif ev_type == "file":
                evidence_text += f"Evidence {i} (file): {ev_content}\n"
            else:
                evidence_text += f"Evidence {i} ({ev_type}): {ev_content}\n"

        prompt = f"""
You are an AI assistant that evaluates whether the provided evidence fulfills the stated goal.
Your response must be a valid JSON object with the following fields:
- approved: boolean (true if the evidence sufficiently meets the goal, false otherwise)
- confidence: a float between 0.0 and 1.0 indicating your confidence in the evaluation
- score: a float between 0.0 and 1.0 representing how well the evidence meets the goal (0.0 = not at all, 1.0 = perfectly)
- reason: a brief string explaining your evaluation
- missing: an array of strings listing what is missing or incomplete in the evidence relative to the goal

Goal:
{goal}

Evidence:
{evidence_text}

Remember to respond with ONLY the JSON object and nothing else.
"""
        return prompt.strip()

    def _parse_response(self, response_text: str) -> VerificationResult:
        """
        Parse the response from the AI, expecting a JSON object.
        If the response is not valid JSON, we try to extract JSON from the text.
        """
        # Try to find a JSON object in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            try:
                data = json.loads(json_str)
                return VerificationResult(
                    approved=data.get("approved", False),
                    confidence=float(data.get("confidence", 0.0)),
                    score=float(data.get("score", 0.0)),
                    reason=data.get("reason", ""),
                    missing=data.get("missing", []),
                )
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                logger.error(f"Failed to parse AI response as JSON: {e}")
                logger.error(f"Response text: {response_text}")
                # Return a default rejected result
                return VerificationResult(approved=False, confidence=0.0, score=0.0, reason="Failed to parse AI response", missing=["AI response parsing error"])
        else:
            logger.error(f"No JSON object found in AI response: {response_text}")
            return VerificationResult(approved=False, confidence=0.0, score=0.0, reason="No JSON found in AI response", missing=["No JSON in response"])

    async def verify_evidence(self, goal: str, evidence_list: list[dict]) -> VerificationResult:
        """
        Verify the evidence against the goal using the AI model.
        """
        if not goal or not evidence_list:
            return VerificationResult(approved=False, confidence=0.0, score=0.0, reason="Goal or evidence is missing", missing=["Goal or evidence missing"])

        prompt = self._build_prompt(goal, evidence_list)
        try:
            # Use the llama client to get a completion
            response = await self.llama_client.chat_completion(
                model="Qwen2.5-VL-7B-Instruct-Q4_K_M",  # This should be configurable
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Lower temperature for more deterministic output
                max_tokens=512,
                top_p=0.9,
                stream=False,
            )
            # Extract the response text
            response_text = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not response_text:
                logger.error("Empty response from AI")
                return VerificationResult(approved=False, confidence=0.0, score=0.0, reason="Empty response from AI", missing=["Empty AI response"])

            return self._parse_response(response_text)
        except Exception as e:
            logger.error(f"Error during AI verification: {e}")
            return VerificationResult(approved=False, confidence=0.0, score=0.0, reason=f"AI verification error: {str(e)}", missing=["AI verification exception"])

# Global service instance
ai_verification_service: Optional[AIVerificationService] = None


def get_ai_verification_service() -> AIVerificationService:
    global ai_verification_service
    if ai_verification_service is None:
        ai_verification_service = AIVerificationService()
    return ai_verification_service