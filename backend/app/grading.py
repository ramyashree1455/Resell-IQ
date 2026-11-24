"""
Dynamic AI Condition Assessment & Grading Engine.
Uses intelligent multi-factor evaluation without hardcoded weights or static question banks.
"""

from typing import Any, Dict, List, Optional
from .services.ai_service import AIService


def get_category_interview(
    category: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Dynamically generates category and item-specific inspection questions
    and camera view prompts using AI.
    """
    return AIService.generate_questions(
        category=category or "general",
        title=title,
        description=description,
    )


def get_grade(score: int) -> str:
    """Standardized grade classification."""
    if score >= 90:
        return "A"
    elif score >= 75:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"


def detect_contradictions(
    answers: Dict[str, Any],
    defects: Optional[List[Dict[str, Any]]] = None,
    transcript: Optional[str] = "",
) -> List[str]:
    """Dynamically detects contradictions between claims, defects, and transcript."""
    evaluation = AIService.evaluate_condition_grade(
        category="general",
        title="product",
        answers=answers,
        defects=defects,
        transcript=transcript or "",
    )
    return evaluation.get("contradictions", [])


def calculate_grade(
    answers: Dict[str, Any],
    defects: Optional[List[Dict[str, Any]]] = None,
    transcript: Optional[str] = "",
    title: Optional[str] = None,
    category: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Dynamically evaluates product condition score, grade (A-D), confidence,
    and explainable reasons using the AI assessment engine.
    """
    return AIService.evaluate_condition_grade(
        category=category or "general",
        title=title or "product",
        answers=answers,
        defects=defects,
        transcript=transcript or "",
    )
