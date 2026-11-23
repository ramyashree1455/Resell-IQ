"""
Interactive AI Seller Interview Service.
Guides sellers through category-specific interviews, camera prompts,
chat-based Q&A, and cross-checks for contradictions.
"""

from typing import Any, Dict, List, Optional
from ..grading import get_category_interview, detect_contradictions, calculate_grade
from .ai_service import AIService


FACTOR_SYNONYMS = {
    "overall_condition": {
        "like_new": ["like new", "brand new", "flawless", "mint", "unboxed", "pristine", "perfect"],
        "excellent": ["excellent", "very good", "barely used", "micro scratch", "super clean"],
        "good": ["good", "normal", "decent", "used", "fine", "minor scuff"],
        "fair": ["fair", "wear", "dings", "scratched", "visible wear"],
        "poor": ["poor", "heavy wear", "battered", "damaged", "dented", "rough"],
    },
    "functional_status": {
        "fully_working": ["fully working", "100%", "perfect", "everything works", "working fine", "no issues", "healthy"],
        "minor_issues": ["minor issue", "battery health low", "speaker crackle", "degraded", "slightly glitchy"],
        "major_issues": ["major issue", "camera blurry", "face id broken", "wifi drops", "touch erratic"],
        "not_working": ["not working", "for parts", "dead", "won't turn on", "broken"],
    },
    "visible_damage": {
        "none": ["none", "no scratches", "no cracks", "flawless", "zero damage", "clean"],
        "minor": ["minor", "light scratch", "hairline", "micro scratches", "faint"],
        "moderate": ["moderate", "visible scratch", "small nick", "bezel scratch", "chipped paint"],
        "major": ["major", "cracked", "crack", "broken glass", "shattered", "dents", "deep scratch"],
    },
    "repair_history": {
        "never_repaired": ["never repaired", "never", "original", "factory parts", "untouched", "no repair"],
        "professionally_repaired": ["professionally repaired", "authorized service", "apple store", "official center"],
        "self_repaired": ["self repaired", "third party", "local shop", "diy"],
        "unknown": ["unknown", "not sure", "previous owner", "second hand"],
    },
    "accessories": {
        "all": ["all", "box and charger", "original box", "complete set", "all included"],
        "some_missing": ["some missing", "charger only", "cable only", "no box"],
        "many_missing": ["device only", "phone only", "bare", "no charger", "many missing"],
        "not_applicable": ["not applicable", "n/a", "none needed"],
    },
}


class InterviewService:
    @staticmethod
    def get_flow(category: Optional[str] = None) -> Dict[str, Any]:
        """Returns category-tailored interview config."""
        return get_category_interview(category)

    @classmethod
    def match_intent(cls, factor: str, message: str) -> Optional[str]:
        """Extract standardized factor value from user's message."""
        cleaned = message.strip().lower()
        synonyms = FACTOR_SYNONYMS.get(factor, {})

        # Direct exact match
        if cleaned in synonyms:
            return cleaned

        # Keyword match
        for standard_val, patterns in synonyms.items():
            for p in patterns:
                if p in cleaned:
                    return standard_val

        return None

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
        Processes one conversational turn of the interview.
        Uses dynamic LLM when configured, otherwise falls back to deterministic NLP.
        """
        # Dynamic LLM turn (if Gemini/OpenAI configured)
        if AIService.is_available() and message:
            llm_res = AIService.analyze_interview_turn(
                category=category,
                item_title=item_title or category,
                message=message,
                step=step,
                answers=answers,
                transcript=transcript,
            )
            if llm_res and "reply" in llm_res:
                updated_answers = dict(answers or {})
                if "extracted_factors" in llm_res and isinstance(llm_res["extracted_factors"], dict):
                    updated_answers.update(llm_res["extracted_factors"])

                new_transcript = f"{transcript}\nA: {message}".strip()
                contradictions = list(llm_res.get("contradictions") or [])
                # Also run core heuristic contradiction detector
                rule_contradictions = detect_contradictions(updated_answers, defects=defects, transcript=new_transcript)
                for rc in rule_contradictions:
                    if rc not in contradictions:
                        contradictions.append(rc)

                return {
                    "reply": llm_res["reply"],
                    "next_step": step + 1,
                    "camera_prompt": llm_res.get("camera_prompt"),
                    "answers": updated_answers,
                    "contradictions": contradictions,
                    "is_complete": bool(llm_res.get("is_complete", len(updated_answers) >= 5)),
                    "transcript": new_transcript,
                }

        config = cls.get_flow(category)
        questions = config["questions"]
        camera_prompts = config["camera_prompts"]
        total_questions = len(questions)

        updated_answers = dict(answers or {})
        transcript_lines = transcript.splitlines() if transcript else []

        # If starting fresh (step 0 with no answer yet or greeting)
        if step == 0 and not message:
            first_q = questions[0]
            first_cam = camera_prompts[0] if camera_prompts else None
            return {
                "reply": f"Hello! Welcome to ReSellIQ's AI verification interview for your {category or 'item'}.\n\n"
                         f"Question 1: {first_q['question']}",
                "next_step": 0,
                "camera_prompt": first_cam,
                "answers": updated_answers,
                "contradictions": [],
                "is_complete": False,
                "transcript": transcript,
            }

        # Handle answer for current question index (min 0, max total_questions - 1)
        current_idx = min(step, total_questions - 1)
        current_q = questions[current_idx]
        factor = current_q["factor"]

        # Parse user answer
        matched_value = cls.match_intent(factor, message)
        if not matched_value:
            # Fallback: take user's raw input
            matched_value = message.strip()

        updated_answers[factor] = matched_value
        transcript_lines.append(f"Q: {current_q['question']}")
        transcript_lines.append(f"A: {message}")

        # Contradiction check
        full_transcript = "\n".join(transcript_lines)
        contradictions = detect_contradictions(updated_answers, defects=defects, transcript=full_transcript)

        next_idx = current_idx + 1
        if next_idx < total_questions:
            next_q = questions[next_idx]
            cam_prompt = camera_prompts[next_idx] if next_idx < len(camera_prompts) else None

            reply = f"Got it. Recorded '{matched_value}'.\n\n"
            if contradictions:
                reply += f"⚠️ Note: A possible contradiction was noticed: {contradictions[-1]}\n\n"
            reply += f"Question {next_idx + 1}: {next_q['question']}"

            return {
                "reply": reply,
                "next_step": next_idx,
                "camera_prompt": cam_prompt,
                "answers": updated_answers,
                "contradictions": contradictions,
                "is_complete": False,
                "transcript": full_transcript,
            }
        else:
            # Finished all questions
            grade_res = calculate_grade(updated_answers, defects=defects, transcript=full_transcript)
            reply = (
                f"Thank you! The AI verification interview is complete.\n\n"
                f"Preliminary Assessment:\n"
                f"- Quality Grade: {grade_res['grade']}\n"
                f"- Condition Score: {grade_res['score']}/100\n"
                f"- Confidence Level: {int(grade_res['confidence'] * 100)}%\n"
            )
            if grade_res["needs_manual_review"]:
                reply += "⚠️ Some items require manual review by admin before final publish.\n"

            return {
                "reply": reply,
                "next_step": total_questions,
                "camera_prompt": None,
                "answers": updated_answers,
                "contradictions": contradictions,
                "is_complete": True,
                "transcript": full_transcript,
            }
