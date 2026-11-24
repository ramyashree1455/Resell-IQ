"""
Grading Service: wraps the condition grading and contradiction detection logic.
"""
from typing import Any, Dict, List, Optional
from .ai_service import AIService


class GradingService:
    @staticmethod
    def grade_product(
        answers: Dict[str, Any],
        defects: Optional[List[Dict[str, Any]]] = None,
        transcript: Optional[str] = "",
        category: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Grade a product dynamically using AI evaluation."""
        return AIService.evaluate_condition_grade(
            category=category or "general",
            title=title or "item",
            answers=answers,
            defects=defects,
            transcript=transcript or "",
        )

    @staticmethod
    def check_contradictions(
        answers: Dict[str, Any],
        defects: Optional[List[Dict[str, Any]]] = None,
        transcript: Optional[str] = "",
    ) -> List[str]:
        """Detect contradictions between claims and evidence."""
        res = AIService.evaluate_condition_grade(
            category="general",
            title="item",
            answers=answers,
            defects=defects,
            transcript=transcript or "",
        )
        return res.get("contradictions", [])

    @staticmethod
    def get_interview_config(
        category: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Retrieve dynamic questions and camera prompts for a given product."""
        return AIService.generate_questions(
            category=category or "general",
            title=title,
            description=description,
        )
