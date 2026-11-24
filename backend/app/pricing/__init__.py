"""
Pricing Feature Module:
- Statistical Fair Price Engine (Median & IQR spread classification)
- Market Comparables Seed Script & Data
- Price Estimation & Benchmark API Router
"""

from .engine import FairPriceEngine, calculate_quartiles, normalize_model_key
from .router import router
from .schemas import (
    GradeBenchmark,
    PriceComparableOut,
    PriceEstimateRequest,
    PriceEstimateResponse,
    SeedPricesResponse,
)
from .seed_data import SEED_DATA, seed_market_comparables

__all__ = [
    "router",
    "FairPriceEngine",
    "seed_market_comparables",
    "calculate_quartiles",
    "normalize_model_key",
    "SEED_DATA",
    "GradeBenchmark",
    "PriceComparableOut",
    "PriceEstimateRequest",
    "PriceEstimateResponse",
    "SeedPricesResponse",
]
