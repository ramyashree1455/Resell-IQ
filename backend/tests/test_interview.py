import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest
from app.database import Base, SessionLocal, engine
from app.models import User, Listing, ConditionReport
from app.schemas import InterviewSubmitRequest, InterviewChatRequest
from app.routers.interview import (
    get_interview_questions,
    submit_interview,
    get_condition_report,
    interview_chat_turn,
)
from app.grading import calculate_grade, get_grade, detect_contradictions
from fastapi import HTTPException


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_grading_pure_function():
    # Flawless condition -> Grade A
    ans_perfect = {
        "overall_condition": "like_new",
        "functional_status": "fully_working",
        "visible_damage": "none",
        "repair_history": "never_repaired",
        "accessories": "all",
    }
    res_perfect = calculate_grade(ans_perfect)
    assert res_perfect["grade"] == "A"
    assert res_perfect["score"] == 100
    assert res_perfect["confidence"] == 1.0
    assert not res_perfect["needs_manual_review"]

    # Heavy wear -> Grade D
    ans_poor = {
        "overall_condition": "poor",
        "functional_status": "not_working",
        "visible_damage": "major",
        "repair_history": "unknown",
        "accessories": "many_missing",
    }
    res_poor = calculate_grade(ans_poor)
    assert res_poor["grade"] == "D"
    assert res_poor["score"] < 40


def test_get_interview_questions():
    # Phone questions
    q_phones = get_interview_questions(category="phones")
    assert q_phones["category"] == "phones"
    assert len(q_phones["camera_prompts"]) > 0
    assert len(q_phones["questions"]) >= 5

    # Laptop questions
    q_laptops = get_interview_questions(category="laptops")
    assert q_laptops["category"] == "laptops"


def test_interview_submit_and_listing_update(setup_db):
    db = setup_db
    seller = User(name="Seller A", email="seller_a@test.com", password_hash="pw", role="seller")
    db.add(seller)
    db.commit()
    db.refresh(seller)

    # 1. Create a listing
    listing = Listing(seller_id=seller.id, category="phones", title="iPhone 13 Pro 128GB", price=45000, location="Bangalore")
    db.add(listing)
    db.commit()
    db.refresh(listing)
    assert listing.grade is None

    # 2. Submit interview answers
    answers = {
        "overall_condition": "excellent",
        "functional_status": "fully_working",
        "visible_damage": "minor",
        "repair_history": "never_repaired",
        "accessories": "all",
    }
    req = InterviewSubmitRequest(
        answers=answers,
        transcript="Seller confirmed pristine screen and OEM charger.",
    )
    res = submit_interview(listing_id=listing.id, data=req, user=seller, db=db)
    assert res["grade"] in ["A", "B"]
    assert res["score"] >= 80
    assert res["confidence"] == 1.0
    assert not res["needs_manual_review"]

    # 3. Verify listing in DB now shows the grade and active status
    db.refresh(listing)
    assert listing.grade == res["grade"]
    assert listing.grade_score == res["score"]
    assert listing.status == "active"

    # 4. Verify Condition Report can be retrieved
    report = get_condition_report(listing_id=listing.id, db=db)
    assert report.grade == res["grade"]
    assert "pristine screen" in report.interview_transcript


def test_low_confidence_requires_manual_review(setup_db):
    db = setup_db
    seller = User(name="Seller B", email="seller_b@test.com", password_hash="pw", role="seller")
    db.add(seller)
    db.commit()
    db.refresh(seller)

    listing = Listing(seller_id=seller.id, category="general", title="Old Desk Lamp", price=500, location="Udupi")
    db.add(listing)
    db.commit()
    db.refresh(listing)

    # Submit only 1 answer (low confidence)
    answers = {"overall_condition": "good"}
    req = InterviewSubmitRequest(answers=answers, transcript="Incomplete answers")
    res = submit_interview(listing_id=listing.id, data=req, user=seller, db=db)
    assert res["needs_manual_review"] is True
    assert res["confidence"] < 0.70

    # Listing status should become "review"
    db.refresh(listing)
    assert listing.status == "review"


def test_unauthorized_user_cannot_grade(setup_db):
    db = setup_db
    seller1 = User(name="Seller 1", email="s1@test.com", password_hash="pw", role="seller")
    seller2 = User(name="Seller 2", email="s2@test.com", password_hash="pw", role="seller")
    db.add_all([seller1, seller2])
    db.commit()
    db.refresh(seller1)
    db.refresh(seller2)

    listing = Listing(seller_id=seller1.id, category="phones", title="Google Pixel 7", price=32000)
    db.add(listing)
    db.commit()
    db.refresh(listing)

    # Seller 2 tries to submit interview for Seller 1's item -> should raise HTTPException(403)
    req = InterviewSubmitRequest(answers={"overall_condition": "like_new"})
    with pytest.raises(HTTPException) as exc:
        submit_interview(listing_id=listing.id, data=req, user=seller2, db=db)
    assert exc.value.status_code == 403


def test_contradiction_detection():
    # 1. Claims "like new" but reports "major" visible damage
    contradictory_answers = {
        "overall_condition": "like_new",
        "functional_status": "fully_working",
        "visible_damage": "major",
        "repair_history": "never_repaired",
        "accessories": "all",
    }
    contradictions = detect_contradictions(contradictory_answers)
    assert len(contradictions) > 0
    assert "visible damage" in contradictions[0].lower()

    # Grading engine should flag manual review and penalize confidence
    res = calculate_grade(contradictory_answers)
    assert res["needs_manual_review"] is True
    assert len(res["contradictions"]) > 0
    assert res["confidence"] < 1.0

    # 2. Claims "never repaired" but transcript shows replacement
    answers_repair_mismatch = {
        "overall_condition": "good",
        "functional_status": "fully_working",
        "visible_damage": "minor",
        "repair_history": "never_repaired",
        "accessories": "all",
    }
    transcript_with_repair = "Seller mentioned that the screen replaced last month at local shop."
    res_mismatch = calculate_grade(answers_repair_mismatch, transcript=transcript_with_repair)
    assert res_mismatch["needs_manual_review"] is True
    assert any("repair" in c.lower() for c in res_mismatch["contradictions"])


def test_interactive_chat_interview_flow(setup_db):
    db = setup_db
    seller = User(name="Chat Seller", email="chat_seller@test.com", password_hash="pw", role="seller")
    db.add(seller)
    db.commit()
    db.refresh(seller)

    listing = Listing(seller_id=seller.id, category="phones", title="OnePlus 11", price=38000)
    db.add(listing)
    db.commit()
    db.refresh(listing)

    # Step 0: Welcome greeting and question 1
    req0 = InterviewChatRequest(message="", step=0, answers={})
    res0 = interview_chat_turn(listing_id=listing.id, data=req0, user=seller, db=db)
    assert "Question 1" in res0["reply"]
    assert res0["camera_prompt"] is not None
    assert not res0["is_complete"]

    # Step 1: Overall condition -> "Flawless and like new"
    req1 = InterviewChatRequest(message="Flawless and like new condition", step=0, answers=res0["answers"])
    res1 = interview_chat_turn(listing_id=listing.id, data=req1, user=seller, db=db)
    assert res1["answers"]["overall_condition"] == "like_new"
    assert res1["next_step"] == 1
    assert "Question 2" in res1["reply"]

    # Step 2: Functional status -> "Everything works 100%"
    req2 = InterviewChatRequest(message="Everything works 100%", step=1, answers=res1["answers"], transcript=res1["transcript"])
    res2 = interview_chat_turn(listing_id=listing.id, data=req2, user=seller, db=db)
    assert res2["answers"]["functional_status"] == "fully_working"
    assert res2["next_step"] == 2

    # Step 3: Visible damage -> "Zero damage, clean"
    req3 = InterviewChatRequest(message="Zero damage, totally clean", step=2, answers=res2["answers"], transcript=res2["transcript"])
    res3 = interview_chat_turn(listing_id=listing.id, data=req3, user=seller, db=db)
    assert res3["answers"]["visible_damage"] == "none"

    # Step 4: Repair history -> "Never repaired, 100% original"
    req4 = InterviewChatRequest(message="Never repaired, 100% original", step=3, answers=res3["answers"], transcript=res3["transcript"])
    res4 = interview_chat_turn(listing_id=listing.id, data=req4, user=seller, db=db)
    assert res4["answers"]["repair_history"] == "never_repaired"

    # Step 5: Accessories -> "All included with original box and charger"
    req5 = InterviewChatRequest(message="All original accessories and box included", step=4, answers=res4["answers"], transcript=res4["transcript"])
    res5 = interview_chat_turn(listing_id=listing.id, data=req5, user=seller, db=db)
    assert res5["answers"]["accessories"] == "all"
    assert res5["is_complete"] is True
    assert "Quality Grade: A" in res5["reply"]

    # Submit final answers to save ConditionReport & update listing
    submit_req = InterviewSubmitRequest(answers=res5["answers"], transcript=res5["transcript"])
    final_res = submit_interview(listing_id=listing.id, data=submit_req, user=seller, db=db)
    assert final_res["grade"] == "A"
    assert final_res["score"] == 100
    assert final_res["confidence"] == 1.0

    db.refresh(listing)
    assert listing.grade == "A"
    assert listing.grade_score == 100
    assert listing.status == "active"


def test_services_layer_grading_service():
    from app.services import GradingService, InterviewService

    config = InterviewService.get_flow("laptops")
    assert config["category"] == "laptops"
    assert len(config["questions"]) >= 5

    grade_result = GradingService.grade_product(
        answers={
            "overall_condition": "excellent",
            "functional_status": "fully_working",
            "visible_damage": "minor",
            "repair_history": "never_repaired",
            "accessories": "all",
        }
    )
    assert grade_result["grade"] in ["A", "B"]
    assert grade_result["score"] >= 80

