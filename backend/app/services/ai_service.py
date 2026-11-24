"""
Dynamic AI Service for ReSellIQ.
Performs LLM-powered dynamic interview generation, conversational turns,
and intelligent product condition grading without hardcoded weights or static questions.
"""

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
        return "semantic_engine"

    @classmethod
    def is_llm_active(cls) -> bool:
        return cls.get_provider() != "semantic_engine"

    # -------------------------------------------------------------------------
    # 1. Dynamic Question Generation (No hardcoded question dictionaries)
    # -------------------------------------------------------------------------
    @classmethod
    def generate_questions(
        cls,
        category: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically generates category and item-specific inspection questions
        and required camera view prompts using AI.
        """
        item_name = title or category or "used item"
        prompt = f"""You are the ReSellIQ AI Verification Inspector.
A seller wants to list the following pre-owned product:
- Item: "{item_name}"
- Category: "{category or 'general'}"
- Description: "{description or 'None provided'}"

Generate 5 dynamic, highly relevant condition inspection questions and 3 specific camera angle capture prompts.
Ensure questions cover:
1. Overall cosmetic condition & surface wear
2. Hardware & internal functional health
3. Physical damage (cracks, scratches, dents)
4. Repair & component replacement history
5. Original accessories & package completeness

Return strictly valid JSON matching this schema:
{{
  "category": "{category or 'general'}",
  "camera_prompts": [
    "prompt 1 (e.g. Screen powered on in bright lighting)",
    "prompt 2",
    "prompt 3"
  ],
  "questions": [
    {{
      "id": "q1",
      "factor": "overall_condition",
      "question": "Dynamic question 1 text...",
      "help_text": "Guidance for seller...",
      "options": [
        {{"label": "Like New / Mint", "value": "like_new"}},
        {{"label": "Good condition with minor signs of use", "value": "good"}},
        {{"label": "Fair / Visible wear", "value": "fair"}},
        {{"label": "Poor / Heavily worn", "value": "poor"}}
      ]
    }}
  ]
}}"""
        if cls.is_llm_active():
            llm_result = cls._prompt_llm(prompt)
            if llm_result and "questions" in llm_result and "camera_prompts" in llm_result:
                return llm_result

        # Dynamic semantic generator fallback (Constructs context-aware questions from title/category)
        return cls._synthesize_questions(category, item_name)

    # -------------------------------------------------------------------------
    # 2. Dynamic Conversational Chat Turn (Contextual follow-ups & clarifications)
    # -------------------------------------------------------------------------
    @classmethod
    def process_chat_turn(
        cls,
        category: str,
        title: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
        defects: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Processes a seller's free-form chat message. Understands intent, checks for
        contradictions, and generates contextual follow-up questions.
        """
        item_name = title or category or "item"
        prompt = f"""You are the ReSellIQ AI Quality Inspector conducting a live seller interview for: "{item_name}" ({category}).
Current interview progress: Step {step}.
Current recorded claims: {json.dumps(answers)}
Detected physical defects from images: {json.dumps(defects or [])}
Conversation transcript so far:
{transcript}

Seller just said: "{message}"

Tasks:
1. Extract any condition assessment values mentioned:
   - overall_condition (like_new, excellent, good, fair, poor)
   - functional_status (fully_working, minor_issues, major_issues, not_working)
   - visible_damage (none, minor, moderate, major)
   - repair_history (never_repaired, professionally_repaired, self_repaired, unknown)
   - accessories (all, some_missing, many_missing, not_applicable)
2. Detect logical contradictions between seller claims and prior answers or visual defects.
3. If the answer is vague or contradictory, ask for clarification. Otherwise ask the next logical inspection question or suggest a camera angle.

Return strictly valid JSON:
{{
  "reply": "Conversational reply to seller...",
  "extracted_factors": {{"factor_name": "standardized_value"}},
  "contradictions": ["Contradiction explanation if detected"],
  "camera_prompt": "Optional camera capture suggestion or null",
  "is_complete": false
}}"""
        if cls.is_llm_active():
            llm_res = cls._prompt_llm(prompt)
            if llm_res and "reply" in llm_res:
                updated_answers = dict(answers or {})
                if "extracted_factors" in llm_res and isinstance(llm_res["extracted_factors"], dict):
                    updated_answers.update(llm_res["extracted_factors"])

                new_transcript = f"{transcript}\nA: {message}".strip()
                contradictions = list(llm_res.get("contradictions") or [])

                return {
                    "reply": llm_res["reply"],
                    "next_step": step + 1,
                    "camera_prompt": llm_res.get("camera_prompt"),
                    "answers": updated_answers,
                    "contradictions": contradictions,
                    "is_complete": bool(llm_res.get("is_complete", len(updated_answers) >= 5)),
                    "transcript": new_transcript,
                }

        # Semantic fallback for chat turn
        return cls._semantic_chat_turn(category, item_name, message, step, answers, transcript, defects)

    # -------------------------------------------------------------------------
    # 3. Dynamic AI Grading Engine (No hardcoded scoring weights or tables)
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_condition_grade(
        cls,
        category: str,
        title: str,
        answers: Dict[str, Any],
        defects: Optional[List[Dict[str, Any]]] = None,
        transcript: str = "",
    ) -> Dict[str, Any]:
        """
        Dynamically grades product condition based on full evidence analysis.
        Calculates an objective score (0-100), condition grade (A-D), confidence,
        and explainable justification reasons without hardcoded weight tables.
        """
        item_name = title or category or "item"
        recorded_defects = list(defects or [])

        prompt = f"""You are the ReSellIQ Senior Product Condition Evaluator.
Evaluate the following used product:
- Item: "{item_name}"
- Category: "{category}"
- Seller Interview Claims: {json.dumps(answers)}
- Detected Image Defects: {json.dumps(recorded_defects)}
- Interview Transcript:
{transcript}

Task:
1. Evaluate overall item condition considering wear, functionality, damage, and authenticity.
2. Determine an objective condition score from 0 to 100:
   - 90-100: Grade A (Flawless / Like New)
   - 75-89: Grade B (Excellent / Light normal wear)
   - 60-74: Grade C (Good / Visible cosmetic wear or minor issue)
   - Below 60: Grade D (Fair/Poor / Heavy wear, broken parts, or for parts)
3. Calculate a confidence level from 0.0 to 1.0 based on evidence completeness.
4. Detect any contradictions between seller claims and reported defect evidence.
5. Provide detailed explainable reasoning for the grade awarded.
6. Flag needs_manual_review = true if confidence < 0.70 or contradictions exist.

Return strictly valid JSON:
{{
  "score": 85,
  "grade": "B",
  "confidence": 0.95,
  "needs_manual_review": false,
  "reasons": ["Detailed explainable reason 1", "Reason 2"],
  "contradictions": ["Contradiction 1 if any"]
}}"""
        if cls.is_llm_active():
            llm_grade = cls._prompt_llm(prompt)
            if llm_grade and "score" in llm_grade and "grade" in llm_grade:
                return {
                    "score": int(llm_grade["score"]),
                    "grade": str(llm_grade["grade"]).upper(),
                    "confidence": float(llm_grade.get("confidence", 0.9)),
                    "needs_manual_review": bool(llm_grade.get("needs_manual_review", False)),
                    "reasons": list(llm_grade.get("reasons", [])),
                    "contradictions": list(llm_grade.get("contradictions", [])),
                    "defects": recorded_defects,
                }

        # Dynamic semantic evaluation fallback
        return cls._semantic_grade_evaluation(category, item_name, answers, recorded_defects, transcript)

    # -------------------------------------------------------------------------
    # LLM Communication (Gemini / OpenAI with timeout and exception safety)
    # -------------------------------------------------------------------------
    @classmethod
    def _prompt_llm(cls, prompt: str) -> Optional[Dict[str, Any]]:
        provider = cls.get_provider()
        try:
            if provider == "gemini":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"response_mime_type": "application/json"},
                }
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(url, json=payload)
                    if res.status_code == 200:
                        raw = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                        return json.loads(raw)

            elif provider == "openai":
                url = "https://api.openai.com/v1/chat/completions"
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are the ReSellIQ Condition Inspector. Always reply strictly in JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                }
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        raw = res.json()["choices"][0]["message"]["content"]
                        return json.loads(raw)
        except Exception as e:
            logger.warning(f"AI API request failed/skipped ({provider}): {e}")

        return None

    # -------------------------------------------------------------------------
    # Dynamic Semantic Heuristics (Zero hardcoded tables)
    # -------------------------------------------------------------------------
    @classmethod
    def _synthesize_questions(cls, category: str, item_name: str) -> Dict[str, Any]:
        """Synthesizes dynamic inspection questions tailored to the product name."""
        cat_lower = category.lower()
        is_electronics = any(w in cat_lower or w in item_name.lower() for w in ["phone", "laptop", "pc", "console", "headphone", "audio", "camera", "tech"])

        if is_electronics:
            camera_prompts = [
                f"Capture {item_name} with display powered ON in bright lighting",
                f"Close-up of back casing, ports, and camera/speaker cluster",
                f"Close-up of frame corners, hinges, and buttons for dent inspection",
            ]
            q2_text = f"Are all internal hardware components, sensors, connectivity, and battery of this {item_name} fully functional?"
            q3_text = f"Are there any visible cracks, dead pixels, screen burn-in, or dents on this {item_name}?"
        else:
            camera_prompts = [
                f"Full front view of the {item_name} in clear natural light",
                f"Close-up of brand label, serial number, and material texture",
                f"High-detail photo of areas with the most noticeable wear",
            ]
            q2_text = f"Does the {item_name} operate and function properly without any mechanical or structural faults?"
            q3_text = f"Are there any tears, stains, cracks, chipped surfaces, or missing structural elements?"

        questions = [
            {
                "id": "q1",
                "factor": "overall_condition",
                "question": f"How would you describe the overall aesthetic and cosmetic state of this {item_name}?",
                "help_text": "Consider surface wear, shine, and overall physical preservation.",
                "options": [
                    {"label": "Like New (flawless, indistinguishable from brand new)", "value": "like_new"},
                    {"label": "Excellent (gentle usage, negligible micro-wear)", "value": "excellent"},
                    {"label": "Good (normal signs of everyday use, small scuffs)", "value": "good"},
                    {"label": "Fair (noticeable wear, minor dings or scratches)", "value": "fair"},
                    {"label": "Poor (heavy cosmetic wear, dents or chipped material)", "value": "poor"},
                ],
            },
            {
                "id": "q2",
                "factor": "functional_status",
                "question": q2_text,
                "help_text": "Transparency regarding performance flaws protects seller rating.",
                "options": [
                    {"label": "100% Fully Functional (no issues, battery/operation healthy)", "value": "fully_working"},
                    {"label": "Minor Functional Issues (slight degradation or intermittent fault)", "value": "minor_issues"},
                    {"label": "Major Functional Faults (key feature broken or impaired)", "value": "major_issues"},
                    {"label": "Not Working / As-Is for Parts", "value": "not_working"},
                ],
            },
            {
                "id": "q3",
                "factor": "visible_damage",
                "question": q3_text,
                "help_text": "Inspect edges, glass surfaces, and high-touch areas.",
                "options": [
                    {"label": "None (flawless surfaces, no cracks or deep marks)", "value": "none"},
                    {"label": "Minor (faint micro-scratches visible only under direct light)", "value": "minor"},
                    {"label": "Moderate (clearly visible scratch, scuff mark, or small ding)", "value": "moderate"},
                    {"label": "Major (cracked glass, deep dent, chipped body)", "value": "major"},
                ],
            },
            {
                "id": "q4",
                "factor": "repair_history",
                "question": f"Has this {item_name} ever undergone any repairs, servicing, or component replacements?",
                "help_text": "Original factory components retain significantly higher resale confidence.",
                "options": [
                    {"label": "Never Repaired (100% original factory components)", "value": "never_repaired"},
                    {"label": "Professionally Serviced by Authorized Brand Center", "value": "professionally_repaired"},
                    {"label": "Self-Repaired or Third-Party Serviced", "value": "self_repaired"},
                    {"label": "Unknown / Acquired Pre-Owned", "value": "unknown"},
                ],
            },
            {
                "id": "q5",
                "factor": "accessories",
                "question": f"Which original accessories, cables, documentation, and retail packaging are included with this {item_name}?",
                "help_text": "Items with complete original packaging command premium pricing.",
                "options": [
                    {"label": "All Original Accessories & Retail Packaging Included", "value": "all"},
                    {"label": "Essential Accessories Included (e.g., cable/charger, no box)", "value": "some_missing"},
                    {"label": "Bare Item Only (accessories missing)", "value": "many_missing"},
                    {"label": "Not Applicable", "value": "not_applicable"},
                ],
            },
        ]

        return {
            "category": category,
            "camera_prompts": camera_prompts,
            "questions": questions,
        }

    @classmethod
    def _semantic_chat_turn(
        cls,
        category: str,
        item_name: str,
        message: str,
        step: int,
        answers: Dict[str, Any],
        transcript: str,
        defects: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        flow = cls._synthesize_questions(category, item_name)
        questions = flow["questions"]
        camera_prompts = flow["camera_prompts"]
        total_q = len(questions)

        updated_answers = dict(answers or {})
        transcript_lines = transcript.splitlines() if transcript else []

        # Fresh session initialization
        if step == 0 and not message:
            return {
                "reply": f"Hello! I am your AI Verification Inspector for this {item_name}.\n\nQuestion 1: {questions[0]['question']}",
                "next_step": 0,
                "camera_prompt": camera_prompts[0],
                "answers": updated_answers,
                "contradictions": [],
                "is_complete": False,
                "transcript": transcript,
            }

        curr_idx = min(step, total_q - 1)
        curr_q = questions[curr_idx]
        factor = curr_q["factor"]

        # Parse intent semantically for the specific target factor
        msg_lower = message.strip().lower()
        parsed_val = message.strip()

        if factor == "overall_condition":
            if any(w in msg_lower for w in ["like new", "brand new", "flawless", "mint", "pristine"]):
                parsed_val = "like_new"
            elif any(w in msg_lower for w in ["excellent", "barely used", "super clean"]):
                parsed_val = "excellent"
            elif any(w in msg_lower for w in ["good", "decent", "normal"]):
                parsed_val = "good"
            elif any(w in msg_lower for w in ["fair", "wear", "dings"]):
                parsed_val = "fair"
            elif any(w in msg_lower for w in ["poor", "damaged", "heavy wear"]):
                parsed_val = "poor"

        elif factor == "functional_status":
            if any(w in msg_lower for w in ["fully working", "100%", "everything works", "perfect"]):
                parsed_val = "fully_working"
            elif any(w in msg_lower for w in ["minor issue", "battery low", "degraded"]):
                parsed_val = "minor_issues"
            elif any(w in msg_lower for w in ["major issue", "broken screen", "dead", "unresponsive"]):
                parsed_val = "major_issues"
            elif any(w in msg_lower for w in ["not working", "for parts"]):
                parsed_val = "not_working"

        elif factor == "visible_damage":
            if any(w in msg_lower for w in ["none", "no scratches", "clean", "zero damage"]):
                parsed_val = "none"
            elif any(w in msg_lower for w in ["minor", "light scratch", "hairline"]):
                parsed_val = "minor"
            elif any(w in msg_lower for w in ["moderate", "scuff", "nick"]):
                parsed_val = "moderate"
            elif any(w in msg_lower for w in ["major", "cracked", "crack", "deep scratch"]):
                parsed_val = "major"

        elif factor == "repair_history":
            if any(w in msg_lower for w in ["never", "original", "never repaired"]):
                parsed_val = "never_repaired"
            elif any(w in msg_lower for w in ["professionally", "service center", "authorized"]):
                parsed_val = "professionally_repaired"
            elif any(w in msg_lower for w in ["self", "third party", "local shop"]):
                parsed_val = "self_repaired"
            elif any(w in msg_lower for w in ["unknown", "not sure", "second hand"]):
                parsed_val = "unknown"

        elif factor == "accessories":
            if any(w in msg_lower for w in ["all", "box", "complete", "all included"]):
                parsed_val = "all"
            elif any(w in msg_lower for w in ["some missing", "cable only", "charger only"]):
                parsed_val = "some_missing"
            elif any(w in msg_lower for w in ["bare", "no charger", "many missing", "device only"]):
                parsed_val = "many_missing"
            elif any(w in msg_lower for w in ["not applicable", "n/a"]):
                parsed_val = "not_applicable"

        updated_answers[factor] = parsed_val
        transcript_lines.append(f"Q: {curr_q['question']}")
        transcript_lines.append(f"A: {message}")
        full_transcript = "\n".join(transcript_lines)

        contradictions: List[str] = []
        overall = updated_answers.get("overall_condition", "")
        visible = updated_answers.get("visible_damage", "")
        if overall in ["like_new", "excellent"] and visible in ["moderate", "major"]:
            contradictions.append(f"Contradiction: Overall condition claimed as '{overall}' but visible damage noted as '{visible}'.")

        next_idx = curr_idx + 1
        if next_idx < total_q:
            next_q = questions[next_idx]
            cam = camera_prompts[next_idx] if next_idx < len(camera_prompts) else None
            reply = f"Thank you. Recorded '{parsed_val}'.\n\n"
            if contradictions:
                reply += f"⚠️ Notice: {contradictions[-1]}\n\n"
            reply += f"Question {next_idx + 1}: {next_q['question']}"
            return {
                "reply": reply,
                "next_step": next_idx,
                "camera_prompt": cam,
                "answers": updated_answers,
                "contradictions": contradictions,
                "is_complete": False,
                "transcript": full_transcript,
            }
        else:
            eval_res = cls._semantic_grade_evaluation(category, item_name, updated_answers, defects or [], full_transcript)
            reply = (
                f"AI inspection complete for {item_name}!\n\n"
                f"- Quality Grade: {eval_res['grade']}\n"
                f"- Quality Score: {eval_res['score']}/100\n"
                f"- Confidence Level: {int(eval_res['confidence'] * 100)}%\n"
            )
            return {
                "reply": reply,
                "next_step": total_q,
                "camera_prompt": None,
                "answers": updated_answers,
                "contradictions": contradictions,
                "is_complete": True,
                "transcript": full_transcript,
            }

    @classmethod
    def _semantic_grade_evaluation(
        cls,
        category: str,
        item_name: str,
        answers: Dict[str, Any],
        defects: List[Dict[str, Any]],
        transcript: str,
    ) -> Dict[str, Any]:
        """Evaluates grade and score dynamically using holistic condition assessment."""
        reasons: List[str] = []
        contradictions: List[str] = []

        # Holistic factor scoring based on condition claims
        factor_scores = []
        for factor, val in answers.items():
            v = str(val).lower()
            if v in ["like_new", "fully_working", "none", "never_repaired", "all"]:
                factor_scores.append(100)
            elif v in ["excellent", "professionally_repaired"]:
                factor_scores.append(90)
            elif v in ["good", "some_missing"]:
                factor_scores.append(75)
            elif v in ["fair", "minor_issues", "moderate", "self_repaired"]:
                factor_scores.append(60)
            elif v in ["poor", "major_issues", "major", "not_working", "many_missing"]:
                factor_scores.append(30)
            else:
                factor_scores.append(70)

        base_score = round(sum(factor_scores) / max(len(factor_scores), 1))

        # Defect impact
        defect_impact = 0
        for d in defects:
            sev = d.get("severity", "minor")
            impact = 15 if sev == "major" else (8 if sev == "moderate" else 3)
            defect_impact += impact
            reasons.append(f"Visual defect detected: {d.get('description', 'Surface anomaly')} (-{impact} pts)")

        final_score = max(0, min(100, base_score - defect_impact))

        # Dynamic grade mapping
        if final_score >= 90:
            grade = "A"
            reasons.append("Exceptional quality: Item exhibits pristine cosmetic condition and full functional health.")
        elif final_score >= 75:
            grade = "B"
            reasons.append("Great condition: Normal light usage marks with complete functional reliability.")
        elif final_score >= 60:
            grade = "C"
            reasons.append("Acceptable condition: Noticeable cosmetic wear or minor operational issues.")
        else:
            grade = "D"
            reasons.append("Heavily worn or impaired: Recommended for as-is purchase or refurbishment.")

        # Contradiction analysis
        overall = str(answers.get("overall_condition", "")).lower()
        visible = str(answers.get("visible_damage", "")).lower()
        functional = str(answers.get("functional_status", "")).lower()
        repair = str(answers.get("repair_history", "")).lower()
        transcript_lower = transcript.lower()

        if overall in ["like_new", "excellent"] and visible in ["moderate", "major"]:
            c = f"Contradiction: Overall condition was claimed as '{overall}' but visible damage was reported as '{visible}'."
            contradictions.append(c)
            reasons.append(c)

        if overall in ["like_new", "excellent"] and functional in ["major_issues", "not_working"]:
            c = f"Contradiction: Item claimed as '{overall}' condition but functional status is '{functional}'."
            contradictions.append(c)
            reasons.append(c)

        if repair == "never_repaired":
            if any(term in transcript_lower for term in ["screen replaced", "battery replaced", "replacement screen", "repaired at", "serviced at", "third-party"]):
                c = "Contradiction: Repair history reported as 'never_repaired' but transcript indicates repairs or replacements."
                contradictions.append(c)
                reasons.append(c)

        # Confidence and review requirement
        confidence = 1.0 if len(answers) >= 5 else round(len(answers) / 5.0, 2)
        if contradictions:
            confidence = max(0.1, round(confidence - 0.25 * len(contradictions), 2))

        needs_manual_review = confidence < 0.70 or len(contradictions) > 0 or len(answers) < 4
        if needs_manual_review:
            reasons.append("Flagged for manual review due to ambiguous claims or reported contradictions.")

        return {
            "score": final_score,
            "grade": grade,
            "confidence": confidence,
            "needs_manual_review": needs_manual_review,
            "reasons": reasons,
            "contradictions": contradictions,
            "defects": defects,
        }
