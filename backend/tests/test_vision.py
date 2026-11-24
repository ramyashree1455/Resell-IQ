"""
Unit and Integration Tests for Vision Feature:
- Perceptual Hashing (dHash) & Duplicate Photo Detection
- Local Computer Vision Defect Detection
- Condition Report Integration
- Vision API Endpoints
"""

import io
import pytest
from PIL import Image, ImageDraw
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import ConditionReport, Listing, ListingImage, User
from app.security import hash_password
from app.vision import (
    DefectDetectionEngine,
    VisionService,
    calculate_hash_similarity,
    compute_dhash,
    hamming_distance,
)

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
client = TestClient(app)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=test_engine)


def create_sample_image(color="blue", draw_crack=False, draw_scratch=False) -> Image.Image:
    img = Image.new("RGB", (200, 200), color=color)
    draw = ImageDraw.Draw(img)
    if draw_crack:
        draw.line((20, 20, 180, 180), fill="white", width=4)
        draw.line((180, 20, 20, 180), fill="white", width=3)
    if draw_scratch:
        draw.line((50, 100, 150, 102), fill="lightgray", width=2)
    return img


def image_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_compute_dhash_format():
    img = create_sample_image("red")
    h = compute_dhash(img)
    assert isinstance(h, str)
    assert len(h) == 16
    int(h, 16)


def test_hamming_distance_exact_match():
    img = create_sample_image("green")
    h1 = compute_dhash(img)
    h2 = compute_dhash(img)
    assert hamming_distance(h1, h2) == 0
    assert calculate_hash_similarity(h1, h2) == 1.0


def test_dhash_resilience_to_scaling():
    img_orig = create_sample_image("purple", draw_crack=True)
    img_scaled = img_orig.resize((100, 100))

    h1 = compute_dhash(img_orig)
    h2 = compute_dhash(img_scaled)

    dist = hamming_distance(h1, h2)
    assert dist <= 4
    sim = calculate_hash_similarity(h1, h2)
    assert sim >= 0.90


def test_dhash_different_images():
    img1 = Image.new("RGB", (100, 100), "white")
    img2 = Image.new("RGB", (100, 100), "black")
    draw = ImageDraw.Draw(img2)
    for x in range(0, 100, 20):
        for y in range(0, 100, 20):
            if (x + y) % 40 == 0:
                draw.rectangle([x, y, x + 20, y + 20], fill="white")

    h1 = compute_dhash(img1)
    h2 = compute_dhash(img2)
    dist = hamming_distance(h1, h2)
    assert dist > 10


def test_duplicate_check_in_db():
    db = TestingSessionLocal()
    seller = User(name="Seller A", email="sellera@test.com", password_hash=hash_password("pw123"))
    db.add(seller)
    db.commit()

    listing1 = Listing(seller_id=seller.id, category="phone", title="Phone 1", price=500.0)
    db.add(listing1)
    db.commit()

    img1 = create_sample_image("cyan", draw_crack=True)
    h1 = compute_dhash(img1)
    db_img1 = ListingImage(
        listing_id=listing1.id,
        url="uploads/cyan_test.jpg",
        view_type="front",
        analysis_json={"perceptual_hash": h1},
    )
    db.add(db_img1)
    db.commit()

    res = VisionService.check_duplicate(db, img1, exclude_listing_id=999)
    assert res.is_duplicate is True
    assert res.matched_listing_id == listing1.id
    assert res.similarity_score >= 0.95


def test_defect_detection_clean_image():
    clean_img = Image.new("RGB", (200, 200), (220, 220, 220))
    result = DefectDetectionEngine.analyze_image(clean_img, view_type="front")
    assert result.is_clean is True
    assert result.defect_count == 0
    assert result.overall_severity == "none"


def test_defect_detection_with_damage():
    damaged_img = create_sample_image("darkblue", draw_crack=True)
    result = DefectDetectionEngine.analyze_image(damaged_img, view_type="screen")
    assert result.is_clean is False
    assert result.defect_count > 0
    assert any(d.type in ["crack", "scratch", "dent"] for d in result.defects)
    for d in result.defects:
        assert 0.0 <= d.location.x <= 1.0
        assert 0.0 <= d.location.y <= 1.0
        assert d.location.width > 0
        assert d.confidence > 0


def test_analyze_listing_images_pipeline():
    db = TestingSessionLocal()
    seller = User(name="Seller B", email="sellerb@test.com", password_hash=hash_password("pw123"))
    db.add(seller)
    db.commit()

    listing = Listing(seller_id=seller.id, category="phone", title="iPhone 13 Tested", price=450.0)
    db.add(listing)
    db.commit()

    report = ConditionReport(listing_id=listing.id, score=92, grade="A", defects_json=[])
    db.add(report)
    db.commit()

    img1 = ListingImage(listing_id=listing.id, url="fake_crack_screen.jpg", view_type="screen")
    img2 = ListingImage(listing_id=listing.id, url="fake_clean_back.jpg", view_type="back")
    db.add_all([img1, img2])
    db.commit()

    vision_report = VisionService.analyze_listing_images(listing_id=listing.id, db=db)

    assert vision_report.listing_id == listing.id
    assert vision_report.total_images == 2
    assert vision_report.condition_report_updated is True

    db.refresh(img1)
    assert img1.analysis_json is not None
    assert "perceptual_hash" in img1.analysis_json

    db.refresh(report)
    assert isinstance(report.defects_json, list)
    assert len(report.defects_json) > 0
    assert report.score < 92
    assert report.grade in ["B", "C", "D"]

    db.refresh(listing)
    assert listing.grade == report.grade
    assert listing.grade_score == report.score


def test_api_vision_detect_defects_file_upload():
    img = create_sample_image("teal", draw_crack=True)
    img_bytes = image_to_bytes(img)

    files = {"file": ("test_phone.jpg", img_bytes, "image/jpeg")}
    data = {"view_type": "front"}
    res = client.post("/vision/detect-defects", files=files, data=data)

    assert res.status_code == 200
    resp_data = res.json()
    assert "perceptual_hash" in resp_data
    assert "defects" in resp_data
    assert isinstance(resp_data["defects"], list)


def test_api_vision_check_duplicate_file_upload():
    img = create_sample_image("magenta")
    img_bytes = image_to_bytes(img)

    files = {"file": ("magenta_phone.jpg", img_bytes, "image/jpeg")}
    res = client.post("/vision/check-duplicate", files=files)

    assert res.status_code == 200
    resp_data = res.json()
    assert "is_duplicate" in resp_data
    assert "perceptual_hash" in resp_data
    assert "similarity_score" in resp_data
