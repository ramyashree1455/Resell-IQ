from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Listing, ConditionReport, User
from ..schemas import (
    InterviewQuestionsResponse,
    InterviewSubmitRequest,
    InterviewChatRequest,
    InterviewChatResponse,
    GradingResultOut,
    ConditionReportOut,
)
from ..grading import get_category_interview, calculate_grade
from ..services.interview_service import InterviewService

router = APIRouter(prefix="/interview", tags=["interview"])


def _get_seller_listing(listing_id: int, user: User, db: Session) -> Listing:
    listing = db.get(Listing, listing_id)
    if not listing or listing.status == "removed":
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to grade this listing")
    return listing


@router.get("/questions", response_model=InterviewQuestionsResponse)
def get_interview_questions(category: Optional[str] = Query(default=None)):
    """
    Fetch category-specific guided interview questions and recommended camera prompts.
    """
    data = get_category_interview(category)
    return data


@router.post("/{listing_id}/chat", response_model=InterviewChatResponse)
def interview_chat_turn(
    listing_id: int,
    data: InterviewChatRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Interactive turn for the AI Seller Interview.
    Processes the seller's chat message, checks for contradictions, prompts for the
    next category question or camera angle, and builds the interview transcript.
    """
    listing = _get_seller_listing(listing_id, user, db)

    chat_result = InterviewService.process_chat_step(
        category=listing.category,
        message=data.message,
        step=data.step,
        answers=data.answers,
        transcript=data.transcript or "",
        defects=data.defects,
    )
    return chat_result


@router.post("/{listing_id}/submit", response_model=GradingResultOut)
def submit_interview(
    listing_id: int,
    data: InterviewSubmitRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit seller answers & interview transcript to grade the listing.
    Calculates condition score (0-100), condition grade (A-D), confidence,
    detects logical contradictions, and saves the ConditionReport.
    Automatically updates Listing.grade, Listing.grade_score,
    and Listing.status ('active' or 'review').
    """
    listing = _get_seller_listing(listing_id, user, db)

    # Run grading engine with contradiction checks
    grading_output = calculate_grade(
        answers=data.answers,
        defects=data.defects,
        transcript=data.transcript or "",
    )

    # API contract: Update listing with grade, score and status
    listing.grade = grading_output["grade"]
    listing.grade_score = grading_output["score"]
    if grading_output["needs_manual_review"]:
        listing.status = "review"
    elif listing.status == "review":
        listing.status = "active"

    # Upsert ConditionReport
    report = db.query(ConditionReport).filter(ConditionReport.listing_id == listing_id).first()
    if not report:
        report = ConditionReport(listing_id=listing_id)
        db.add(report)

    report.score = grading_output["score"]
    report.grade = grading_output["grade"]
    report.confidence = grading_output["confidence"]
    report.defects_json = grading_output["defects"]
    report.interview_transcript = data.transcript or ""

    db.commit()
    db.refresh(listing)
    db.refresh(report)

    return {
        "score": grading_output["score"],
        "grade": grading_output["grade"],
        "confidence": grading_output["confidence"],
        "needs_manual_review": grading_output["needs_manual_review"],
        "reasons": grading_output["reasons"],
        "contradictions": grading_output.get("contradictions", []),
        "report": report,
    }


@router.get("/{listing_id}/report", response_model=ConditionReportOut)
def get_condition_report(listing_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the verified AI condition report for a listing.
    """
    listing = db.get(Listing, listing_id)
    if not listing or listing.status == "removed":
        raise HTTPException(status_code=404, detail="Listing not found")

    report = db.query(ConditionReport).filter(ConditionReport.listing_id == listing_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Condition report not found for this listing")

    return report
