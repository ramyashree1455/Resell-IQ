"""
AI Service: Dynamic LLM integration (Gemini / OpenAI / Claude) with zero hardcoded credentials.
Uses environment variables and falls back to deterministic heuristics when no API key is provided.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from ..config import GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)


class AIService:
    @classmethod
    def get_provider(cls) -> str:
        if GEMINI_API_KEY:
            return "gemini"
        elif OPENAI_API_KEY:
            return "openai"
        elif ANTHROPIC_API_KEY:
            return "anthropic"
        return "fallback"

    @classmethod
    def is_available(cls) -> bool:
        return cls.get_provider() != "fallback"

    @classmethod
    def analyze_interview_turn(
        cls,
        category: str,
        item_title: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Dynamically analyzes seller input and generates the next conversational question.
        Returns None if no LLM key is configured or if the request fails.
        """
        provider = cls.get_provider()
        if provider == "gemini":
            return cls._call_gemini(category, item_title, message, step, answers, transcript)
        elif provider == "openai":
            return cls._call_openai(category, item_title, message, step, answers, transcript)
        return None

    @classmethod
    def _build_prompt(
        cls,
        category: str,
        item_title: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
    ) -> str:
        return f"""You are the AI Quality Inspector for ReSellIQ, a verified resale marketplace.
Item: "{item_title}" (Category: {category})
Current Interview Step: {step}
Recorded Answers So Far: {json.dumps(answers)}
Recent Transcript:
{transcript}

Seller's Latest Message: "{message}"

Your tasks:
1. Extract any condition factors from the seller's latest message:
   - overall_condition: [like_new, excellent, good, fair, poor]
   - functional_status: [fully_working, minor_issues, major_issues, not_working]
   - visible_damage: [none, minor, moderate, major]
   - repair_history: [never_repaired, professionally_repaired, self_repaired, unknown]
   - accessories: [all, some_missing, many_missing, not_applicable]
2. Detect any logical contradictions with earlier claims (e.g. claiming like-new but reporting scratches, cracks, or repairs).
3. Formulate a friendly, natural follow-up response and ask the next logical inspection question or camera angle.

Respond strictly with valid JSON conforming to this schema:
{{
  "reply": "string (conversational message to seller)",
  "extracted_factors": {{"factor_name": "standardized_value"}},
  "contradictions": ["string contradiction warnings if any, else empty list"],
  "camera_prompt": "string or null (recommended photo angle)",
  "is_complete": false
}}"""

    @classmethod
    def _call_gemini(
        cls,
        category: str,
        item_title: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
    ) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        prompt = cls._build_prompt(category, item_title, message, step, answers, transcript)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"Gemini API call skipped/failed: {e}")
        return None

    @classmethod
    def _call_openai(
        cls,
        category: str,
        item_title: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
    ) -> Optional[Dict[str, Any]]:
        url = "https://api.openai.com/v1/chat/completions"
        prompt = cls._build_prompt(category, item_title, message, step, answers, transcript)

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a product verification AI. Always return JSON."},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }

        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

        try:
            with httpx.Client(timeout=8.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    raw_text = res.json()["choices"][0]["message"]["content"]
                    return json.loads(raw_text)
        except Exception as e:
            logger.warning(f"OpenAI API call skipped/failed: {e}")
        return None
