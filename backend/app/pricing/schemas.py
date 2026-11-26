"""
Pricing Feature Pydantic Schemas.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class PriceEstimateRequest(BaseModel):
    model_key: str = Field(..., min_length=2, max_length=500, description="e.g. 'iPhone 13 128GB' or 'MacBook Air M1'")
    grade: str = Field(..., pattern="^[A-Da-d]$", description="Condition grade: A, B, C, or D")
    asking_price: float = Field(..., gt=0, description="Asking price in INR or dollars")
    currency: Optional[str] = Field(None, description="Optional currency: INR or USD")
    mrp: Optional[float] = Field(None, gt=0, description="Optional original retail M.R.P. from listing")


class GradeBenchmark(BaseModel):
    grade: str
    median_price: float
    min_price: float
    max_price: float
    sample_size: int


class PriceEstimateResponse(BaseModel):
    model_key: str
    grade: str
    asking_price: float
    verdict: str = Field(..., description="'Great deal' | 'Fair' | 'Overpriced'")
    market_median: float
    fair_range_min: float
    fair_range_max: float
    iqr: float
    sample_size: int
    confidence: float
    diff_from_median: float
    percentage_vs_median: float
    explanation: str
    grade_benchmarks: List[GradeBenchmark] = []


class PriceComparableOut(BaseModel):
    id: int
    model_key: str
    grade: str
    price: float
    sold_at: datetime
    model_config = {"from_attributes": True}


class SeedPricesResponse(BaseModel):
    message: str
    inserted_count: int
    total_records: int
    categories_seeded: List[str]
