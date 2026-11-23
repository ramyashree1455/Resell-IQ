"""
Seller-reported product condition grading engine & AI interview questionnaire.

Calculates:
- Category-specific interview questions & camera prompts
- Condition score (0-100)
- Condition grade (A-D)
- Confidence (0.0-1.0)
- Manual review requirement
"""

from typing import Any, Dict, List, Optional


# Importance of each condition factor
WEIGHTS = {
    "overall_condition": 30,
    "functional_status": 30,
    "visible_damage": 25,
    "repair_history": 10,
    "accessories": 5,
}


# Points awarded for each answer
SCORING = {
    "overall_condition": {
        "like_new": 100,
        "excellent": 90,
        "good": 75,
        "fair": 55,
        "poor": 25,
    },
    "functional_status": {
        "fully_working": 100,
        "minor_issues": 65,
        "major_issues": 30,
        "not_working": 0,
    },
    "visible_damage": {
        "none": 100,
        "minor": 80,
        "moderate": 50,
        "major": 15,
    },
    "repair_history": {
        "never_repaired": 100,
        "professionally_repaired": 75,
        "self_repaired": 50,
        "unknown": 40,
    },
    "accessories": {
        "all": 100,
        "some_missing": 65,
        "many_missing": 30,
        "not_applicable": 100,
    },
}


CATEGORY_INTERVIEW_CONFIGS = {
    "phones": {
        "camera_prompts": [
            "Screen powered on showing home screen or white background",
            "Back panel and camera lens cluster in clear lighting",
            "Close-up of all four edges/corners and charging port",
        ],
        "questions": [
            {
                "id": "q1",
                "factor": "overall_condition",
                "question": "How would you describe the overall aesthetic state of the phone?",
                "help_text": "Consider scratches, body shine, and overall feel.",
                "options": [
                    {"label": "Like New (flawless, indistinguishable from unboxed)", "value": "like_new"},
                    {"label": "Excellent (very faint micro-scratches barely visible)", "value": "excellent"},
                    {"label": "Good (normal signs of everyday use, small scuffs)", "value": "good"},
                    {"label": "Fair (noticeable wear, minor dings on frame)", "value": "fair"},
                    {"label": "Poor (heavy cosmetic wear, dents or chipped edges)", "value": "poor"},
                ],
            },
            {
                "id": "q2",
                "factor": "functional_status",
                "question": "Are all hardware features functioning normally (touchscreen, FaceID/fingerprint, cameras, speakers, Wi-Fi)?",
                "help_text": "Be transparent about any intermittent glitches or battery issues.",
                "options": [
                    {"label": "100% Fully Working (all sensors, cameras & touch perfect)", "value": "fully_working"},
                    {"label": "Minor Issues (e.g., degraded battery health < 80%, slight speaker crackle)", "value": "minor_issues"},
                    {"label": "Major Issues (e.g., FaceID broken, camera blurry, Wi-Fi drops)", "value": "major_issues"},
                    {"label": "Not Working / For Parts", "value": "not_working"},
                ],
            },
            {
                "id": "q3",
                "factor": "visible_damage",
                "question": "Is there any visible physical damage on the display, glass back, or camera lens?",
                "help_text": "Include hairline cracks, deep scratches, or dents.",
                "options": [
                    {"label": "None (no cracks, no deep scratches)", "value": "none"},
                    {"label": "Minor (light scratches only visible under direct light)", "value": "minor"},
                    {"label": "Moderate (visible scratch or small nick on bezel)", "value": "moderate"},
                    {"label": "Major (cracked screen, back glass crack, camera lens broken)", "value": "major"},
                ],
            },
            {
                "id": "q4",
                "factor": "repair_history",
                "question": "Has this device ever undergone any screen replacement or component repairs?",
                "help_text": "Original OEM parts retain much higher resale value.",
                "options": [
                    {"label": "Never Repaired (100% original factory components)", "value": "never_repaired"},
                    {"label": "Professionally Repaired by Authorized Service Center", "value": "professionally_repaired"},
                    {"label": "Repaired at Third-Party Shop or Self-Repaired", "value": "self_repaired"},
                    {"label": "Unknown / Previous Owner history", "value": "unknown"},
                ],
            },
            {
                "id": "q5",
                "factor": "accessories",
                "question": "Which original accessories and packaging are included?",
                "help_text": "Original retail box, charging cable, and adapter.",
                "options": [
                    {"label": "All Included (original box + cable/adapter)", "value": "all"},
                    {"label": "Some Missing (cable only, no retail box)", "value": "some_missing"},
                    {"label": "Many Missing (device only)", "value": "many_missing"},
                    {"label": "Not Applicable", "value": "not_applicable"},
                ],
            },
        ],
    },
    "laptops": {
        "camera_prompts": [
            "Screen turned on showing bright display to check for dead pixels",
            "Top lid closed and bottom case inspection",
            "Keyboard and trackpad area in clear light",
            "Close-up of side ports and display hinges",
        ],
        "questions": [
            {
                "id": "q1",
                "factor": "overall_condition",
                "question": "What is the overall exterior physical condition of the laptop?",
                "help_text": "Inspect lid, palm rest, and base.",
                "options": [
                    {"label": "Like New (pristine condition)", "value": "like_new"},
                    {"label": "Excellent (gentle office use only)", "value": "excellent"},
                    {"label": "Good (minor keyboard shine, light base scratches)", "value": "good"},
                    {"label": "Fair (rub marks, small chassis dings)", "value": "fair"},
                    {"label": "Poor (cracked plastic, bent metal casing)", "value": "poor"},
                ],
            },
            {
                "id": "q2",
                "factor": "functional_status",
                "question": "How are the keyboard, trackpad, ports, and battery performance?",
                "help_text": "Checks keypress reliability and battery backup.",
                "options": [
                    {"label": "Fully Functional (healthy battery, all keys & ports work)", "value": "fully_working"},
                    {"label": "Minor Issues (battery lasts < 1 hour or one sticky key)", "value": "minor_issues"},
                    {"label": "Major Issues (must stay plugged in, trackpad erratic, bad fan)", "value": "major_issues"},
                    {"label": "Not Working / Boots to BIOS only", "value": "not_working"},
                ],
            },
            {
                "id": "q3",
                "factor": "visible_damage",
                "question": "Are there display defects (dead pixels, lines, pressure marks) or hinge issues?",
                "help_text": "Examine the screen closely on a light background.",
                "options": [
                    {"label": "None (flawless display & firm hinge)", "value": "none"},
                    {"label": "Minor (micro keyboard marks on screen coating)", "value": "minor"},
                    {"label": "Moderate (loose hinge or small bright spot on LCD)", "value": "moderate"},
                    {"label": "Major (cracked screen, dead lines, broken hinge)", "value": "major"},
                ],
            },
            {
                "id": "q4",
                "factor": "repair_history",
                "question": "Has this laptop had its motherboard, battery, or screen replaced?",
                "help_text": "Mention any warranty or DIY servicing.",
                "options": [
                    {"label": "Never Repaired / Serviced", "value": "never_repaired"},
                    {"label": "Professionally Serviced (brand authorized)", "value": "professionally_repaired"},
                    {"label": "Self or Third-Party Serviced", "value": "self_repaired"},
                    {"label": "Unknown", "value": "unknown"},
                ],
            },
            {
                "id": "q5",
                "factor": "accessories",
                "question": "Do you have the original OEM charger and packaging?",
                "help_text": "Genuine power brick prevents device wear.",
                "options": [
                    {"label": "Original OEM Charger + Box included", "value": "all"},
                    {"label": "Original Charger included, no box", "value": "some_missing"},
                    {"label": "Generic / third-party charger only", "value": "many_missing"},
                    {"label": "No charger included", "value": "many_missing"},
                ],
            },
        ],
    },
    "default": {
        "camera_prompts": [
            "Front view in well-lit surroundings",
            "Back and side panels",
            "Close-up of brand label, serial number, or any noticeable wear",
        ],
        "questions": [
            {
                "id": "q1",
                "factor": "overall_condition",
                "question": "How would you rate the overall cosmetic condition?",
                "help_text": "Appearance, cleanliness, and wear.",
                "options": [
                    {"label": "Like New (hardly used, looks brand new)", "value": "like_new"},
                    {"label": "Excellent (very light wear)", "value": "excellent"},
                    {"label": "Good (normal signs of use)", "value": "good"},
                    {"label": "Fair (visible scratches or cosmetic wear)", "value": "fair"},
                    {"label": "Poor (heavy wear or damage)", "value": "poor"},
                ],
            },
            {
                "id": "q2",
                "factor": "functional_status",
                "question": "Does the item function as intended?",
                "help_text": "Is it completely operational without defects?",
                "options": [
                    {"label": "100% Fully Working", "value": "fully_working"},
                    {"label": "Minor Functional Issues", "value": "minor_issues"},
                    {"label": "Major Functional Faults", "value": "major_issues"},
                    {"label": "Not Working / As-Is", "value": "not_working"},
                ],
            },
            {
                "id": "q3",
                "factor": "visible_damage",
                "question": "Is there any noticeable visible damage, cracks, or dents?",
                "help_text": "Check all surfaces and edges.",
                "options": [
                    {"label": "None", "value": "none"},
                    {"label": "Minor (surface scuffs)", "value": "minor"},
                    {"label": "Moderate (visible scratches or dents)", "value": "moderate"},
                    {"label": "Major (cracks, deep scratches, missing parts)", "value": "major"},
                ],
            },
            {
                "id": "q4",
                "factor": "repair_history",
                "question": "Has this item ever undergone repair or alteration?",
                "help_text": "Past maintenance and service history.",
                "options": [
                    {"label": "Never Repaired", "value": "never_repaired"},
                    {"label": "Professionally Repaired", "value": "professionally_repaired"},
                    {"label": "Self / Third-party Repaired", "value": "self_repaired"},
                    {"label": "Unknown", "value": "unknown"},
                ],
            },
            {
                "id": "q5",
                "factor": "accessories",
                "question": "Are all standard accessories and manuals included?",
                "help_text": "Cables, attachments, remote controls, or box.",
                "options": [
                    {"label": "All Original Accessories Included", "value": "all"},
                    {"label": "Some Accessories Missing", "value": "some_missing"},
                    {"label": "Bare Item Only", "value": "many_missing"},
                    {"label": "Not Applicable", "value": "not_applicable"},
                ],
            },
        ],
    },
}


def get_category_interview(category: Optional[str] = None) -> Dict[str, Any]:
    """Return interview questions and camera prompts for a given listing category."""
    cat_key = (category or "").strip().lower()
    if cat_key in CATEGORY_INTERVIEW_CONFIGS:
        cfg = CATEGORY_INTERVIEW_CONFIGS[cat_key]
    elif "phone" in cat_key or "mobile" in cat_key:
        cfg = CATEGORY_INTERVIEW_CONFIGS["phones"]
    elif "laptop" in cat_key or "pc" in cat_key or "computer" in cat_key:
        cfg = CATEGORY_INTERVIEW_CONFIGS["laptops"]
    else:
        cfg = CATEGORY_INTERVIEW_CONFIGS["default"]

    return {
        "category": cat_key or "general",
        "camera_prompts": cfg["camera_prompts"],
        "questions": cfg["questions"],
    }


def get_grade(score: int) -> str:
    """Convert a numerical score into a condition grade."""
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
    """
    Detect logical contradictions between seller claims, defects, and transcript.
    Used for automated fraud deterrence and evaluation benchmarks.
    """
    contradictions: List[str] = []
    overall = (answers.get("overall_condition") or "").strip().lower()
    functional = (answers.get("functional_status") or "").strip().lower()
    visible = (answers.get("visible_damage") or "").strip().lower()
    repair = (answers.get("repair_history") or "").strip().lower()
    defects_list = list(defects or [])
    transcript_lower = (transcript or "").lower()

    # 1. Like new / excellent but moderate/major visible damage
    if overall in ["like_new", "excellent"] and visible in ["moderate", "major"]:
        contradictions.append(
            f"Contradiction: Overall condition claimed as '{overall}' but visible damage reported as '{visible}'."
        )

    # 2. Like new / excellent but major functional issues or not working
    if overall in ["like_new", "excellent"] and functional in ["major_issues", "not_working"]:
        contradictions.append(
            f"Contradiction: Overall condition claimed as '{overall}' but functional status is '{functional}'."
        )

    # 3. Visible damage claimed as none, but physical defects submitted
    if visible == "none" and len(defects_list) > 0:
        contradictions.append(
            f"Contradiction: Visible damage claimed as 'none' but {len(defects_list)} defect(s) were submitted."
        )

    # 4. Fully working claimed, but critical defect listed
    if functional == "fully_working":
        for d in defects_list:
            text = f"{d.get('description', '')} {d.get('type', '')} {d.get('label', '')}".lower()
            if any(term in text for term in ["broken", "dead", "unresponsive", "shattered", "not turning on"]):
                contradictions.append(
                    f"Contradiction: Functional status reported as 'fully_working' but defect specifies '{d.get('description') or d.get('type')}'."
                )
                break

    # 5. Never repaired claimed, but repair mentioned in transcript
    if repair == "never_repaired":
        repair_triggers = [
            "screen replaced",
            "battery replaced",
            "replacement screen",
            "third-party repair",
            "third party repair",
            "was repaired",
            "got repaired",
            "repaired by",
            "repaired at",
            "had it repaired",
            "serviced at",
        ]
        for trigger in repair_triggers:
            if trigger in transcript_lower:
                contradictions.append(
                    f"Contradiction: Repair history reported as 'never_repaired' but transcript mentions '{trigger}'."
                )
                break

    return contradictions


def calculate_grade(
    answers: Dict[str, Any],
    defects: Optional[List[Dict[str, Any]]] = None,
    transcript: Optional[str] = "",
) -> Dict[str, Any]:
    """
    Calculate the product condition score, grade, confidence, and manual review flag.

    Expected answer keys:
    overall_condition, functional_status, visible_damage, repair_history, accessories
    """
    total_weight = sum(WEIGHTS.values())

    weighted_score = 0
    answered_weight = 0
    valid_answers = 0
    reasons: List[str] = []
    recorded_defects: List[Dict[str, Any]] = list(defects or [])

    for factor, weight in WEIGHTS.items():
        answer = answers.get(factor)

        if not isinstance(answer, str):
            reasons.append(f"Missing answer: {factor}")
            continue

        answer = answer.strip().lower()
        points = SCORING[factor].get(answer)

        if points is None:
            reasons.append(f"Invalid or unrecognized answer: {factor}")
            continue

        weighted_score += points * weight
        answered_weight += weight
        valid_answers += 1

    # Base score using answered factors
    if answered_weight == 0:
        score = 0
    else:
        score = round(weighted_score / answered_weight)

    # Defect deductions (if vision analysis or seller self-reported specific defects)
    defect_penalty = 0
    for defect in recorded_defects:
        severity = defect.get("severity", "minor")
        if severity == "major":
            defect_penalty += 15
        elif severity == "moderate":
            defect_penalty += 8
        else:
            defect_penalty += 3

    if defect_penalty > 0:
        reasons.append(f"Deducted {defect_penalty} points for {len(recorded_defects)} reported defect(s)")
        score = max(0, score - defect_penalty)

    grade = get_grade(score)

    # Confidence depends on factor completion
    confidence = round(answered_weight / total_weight, 2)

    # Contradiction detection
    contradictions = detect_contradictions(answers, recorded_defects, transcript)
    if contradictions:
        # Penalize confidence for each logical contradiction
        confidence = max(0.1, round(confidence - 0.25 * len(contradictions), 2))
        for c in contradictions:
            reasons.append(c)

    # Flag for manual review if answers are sparse, confidence is low, or contradictions exist
    needs_manual_review = valid_answers < 4 or confidence < 0.70 or len(contradictions) > 0

    if needs_manual_review:
        if len(contradictions) > 0:
            reasons.append(f"Flagged for manual review due to {len(contradictions)} contradiction(s)")
        else:
            reasons.append("Insufficient information for high-confidence grading: marked for manual review")

    return {
        "score": score,
        "grade": grade,
        "confidence": confidence,
        "needs_manual_review": needs_manual_review,
        "reasons": reasons,
        "defects": recorded_defects,
        "contradictions": contradictions,
    }
