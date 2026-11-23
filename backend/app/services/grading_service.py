"""
Grading Service: wraps the condition grading and contradiction detection logic.
"""
from typing import Any, Dict, List, Optional
from ..grading import calculate_grade, detect_contradictions, get_category_interview, get_grade


class GradingService:
    @staticmethod
    def grade_product(
        answers: Dict[str, Any],
        defects: Optional[List[Dict[str, Any]]] = None,
        transcript: Optional[str] = "",
    ) -> Dict[str, Any]:
        """Grade a product given seller answers, defects, and optional transcript."""
        return calculate_grade(answers=answers, defects=defects, transcript=transcript)

    @staticmethod
    def check_contradictions(
        answers: Dict[str, Any],
        defects: Optional[List[Dict[str, Any]]] = None,
        transcript: Optional[str] = "",
    ) -> List[str]:
        """Detect contradictions between claims and evidence."""
        return detect_contradictions(answers=answers, defects=defects, transcript=transcript)

    @staticmethod
    def get_interview_config(category: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve questions and camera prompts for a given category."""
        return get_category_interview(category)
