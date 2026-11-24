"""
Pricing Feature Router.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PriceComparable
from .engine import FairPriceEngine
from .schemas import (
    PriceComparableOut,
    PriceEstimateRequest,
    PriceEstimateResponse,
    SeedPricesResponse,
)
from .seed_data import seed_market_comparables

router = APIRouter(prefix="/price", tags=["pricing"])


@router.get("/estimate", response_model=PriceEstimateResponse)
def estimate_price_get(
    model_key: str = Query(..., min_length=2, max_length=150, description="e.g. 'iPhone 13'"),
    grade: str = Query(..., pattern="^[A-Da-d]$", description="Grade A, B, C, or D"),
    asking_price: float = Query(..., gt=0, description="Asking price in dollars"),
    db: Session = Depends(get_db),
):
    """
    Evaluates an asking price against statistical historical market comparables (GET).
    Returns verdict ('Great deal', 'Fair', 'Overpriced'), market median, IQR spread,
    and cross-grade comparison.
    """
    try:
        return FairPriceEngine.evaluate(
            model_key=model_key,
            grade=grade,
            asking_price=asking_price,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/estimate", response_model=PriceEstimateResponse)
def estimate_price_post(
    req: PriceEstimateRequest,
    db: Session = Depends(get_db),
):
    """
    Evaluates an asking price against statistical historical market comparables (POST).
    """
    try:
        return FairPriceEngine.evaluate(
            model_key=req.model_key,
            grade=req.grade,
            asking_price=req.asking_price,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/seed", response_model=SeedPricesResponse)
def seed_prices_endpoint(
    overwrite: bool = Query(False, description="Whether to overwrite existing seed data"),
    db: Session = Depends(get_db),
):
    """
    Populates PriceComparable table with 60+ realistic historical transactions.
    """
    inserted = seed_market_comparables(db=db, overwrite=overwrite)
    total = db.query(PriceComparable).count()
    categories = ["smartphones", "laptops", "tablets", "audio"]
    return SeedPricesResponse(
        message=f"Successfully seeded price comparables database with realistic market benchmarks.",
        inserted_count=inserted,
        total_records=total,
        categories_seeded=categories,
    )


@router.get("/comparables", response_model=List[PriceComparableOut])
def get_price_comparables(
    model_key: Optional[str] = Query(None, description="Filter by model keyword"),
    grade: Optional[str] = Query(None, pattern="^[A-Da-d]$", description="Filter by grade"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Queries historical sales transactions from the PriceComparable table.
    """
    q = db.query(PriceComparable)
    if model_key:
        q = q.filter(PriceComparable.model_key.ilike(f"%{model_key.strip()}%"))
    if grade:
        q = q.filter(PriceComparable.grade.ilike(grade.strip()))
    return q.order_by(PriceComparable.sold_at.desc()).limit(limit).all()
