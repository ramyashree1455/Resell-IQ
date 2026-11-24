"""
Unit and Integration Tests for Pricing Feature:
- Fair Price Engine & Benchmark Spread Calculations
- Seed Data Script & Data Quality
- Pricing API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.pricing import (
    FairPriceEngine,
    seed_market_comparables,
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
    db = TestingSessionLocal()
    seed_market_comparables(db, overwrite=True)
    yield
    app.dependency_overrides.pop(get_db, None)
    Base.metadata.drop_all(bind=test_engine)


def test_fair_price_great_deal():
    db = TestingSessionLocal()
    res = FairPriceEngine.evaluate(
        model_key="iPhone 13",
        grade="A",
        asking_price=380.0,
        db=db,
    )
    assert res.verdict == "Great deal"
    assert res.asking_price == 380.0
    assert res.market_median >= 450.0
    assert res.diff_from_median < 0
    assert "below the market median" in res.explanation
    assert len(res.grade_benchmarks) == 4


def test_fair_price_fair():
    db = TestingSessionLocal()
    res = FairPriceEngine.evaluate(
        model_key="iPhone 13",
        grade="A",
        asking_price=478.0,
        db=db,
    )
    assert res.verdict == "Fair"
    assert "fair market range" in res.explanation


def test_fair_price_overpriced():
    db = TestingSessionLocal()
    res = FairPriceEngine.evaluate(
        model_key="iPhone 13",
        grade="B",
        asking_price=580.0,
        db=db,
    )
    assert res.verdict == "Overpriced"
    assert res.diff_from_median > 0
    assert "above the market median" in res.explanation


def test_fair_price_cross_grade_gradient():
    db = TestingSessionLocal()
    res = FairPriceEngine.evaluate(
        model_key="MacBook Air M1",
        grade="A",
        asking_price=640.0,
        db=db,
    )
    grades_dict = {b.grade: b.median_price for b in res.grade_benchmarks}
    assert grades_dict["A"] > grades_dict["B"] > grades_dict["C"] > grades_dict["D"]


def test_api_price_estimate_get():
    res = client.get("/price/estimate?model_key=iPhone+13&grade=A&asking_price=400")
    assert res.status_code == 200
    data = res.json()
    assert data["model_key"] == "iPhone 13"
    assert data["grade"] == "A"
    assert data["verdict"] in ["Great deal", "Fair", "Overpriced"]
    assert "fair_range_min" in data
    assert "market_median" in data


def test_api_price_estimate_post():
    payload = {"model_key": "Dell XPS 13", "grade": "B", "asking_price": 600.0}
    res = client.post("/price/estimate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["model_key"] == "Dell XPS 13"
    assert data["verdict"] == "Fair"


def test_api_price_comparables_query():
    res = client.get("/price/comparables?model_key=MacBook&limit=10")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) > 0
    assert all("MacBook" in it["model_key"] for it in items)


def test_api_price_seed():
    res = client.post("/price/seed?overwrite=true")
    assert res.status_code == 200
    data = res.json()
    assert data["inserted_count"] > 50
    assert data["total_records"] > 50
