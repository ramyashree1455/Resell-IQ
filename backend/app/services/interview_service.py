"""
Interactive AI Seller Interview Service.
Guides sellers through dynamic product interviews, camera prompts,
chat-based Q&A, and cross-checks for contradictions.
"""

from typing import Any, Dict, List, Optional
from .ai_service import AIService


class InterviewService:
    @staticmethod
    def get_flow(
        category: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Returns dynamic AI-generated interview questions and camera prompts."""
        return AIService.generate_questions(
            category=category or "general",
            title=title,
            description=description,
        )

    @classmethod
    def process_chat_step(
        cls,
        category: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str = "",
        defects: Optional[List[Dict[str, Any]]] = None,
        item_title: str = "",
    ) -> Dict[str, Any]:
        """
        Processes one conversational turn of the interview dynamically using AI.
        """
        return AIService.process_chat_turn(
            category=category,
            title=item_title or category,
            message=message,
            step=step,
            answers=answers,
            transcript=transcript,
            defects=defects,
        )
