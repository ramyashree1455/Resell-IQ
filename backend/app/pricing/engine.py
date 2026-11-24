"""
Fair Price Engine:
Calculates statistical median and spread by model_key and condition grade (A, B, C, D).
Classifies asking price as 'Great deal', 'Fair', or 'Overpriced'.
Provides transparent market benchmarks and cross-grade price comparisons.
"""

import math
import statistics
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import PriceComparable
from .schemas import GradeBenchmark, PriceEstimateResponse


def normalize_model_key(raw_key: str) -> str:
    """Normalizes model keys (e.g., '  Apple iPhone 13  ' -> 'iphone 13')."""
    cleaned = raw_key.strip().lower()
    prefixes = ["apple ", "samsung ", "google ", "dell ", "sony ", "lenovo "]
    for p in prefixes:
        if cleaned.startswith(p):
            cleaned = cleaned[len(p):].strip()
    return cleaned


def calculate_quartiles(values: List[float]) -> Tuple[float, float, float, float]:
    """Calculates median, Q1 (25th percentile), Q3 (75th percentile), and IQR."""
    if not values:
        return 0.0, 0.0, 0.0, 0.0
    sorted_v = sorted(values)
    med = statistics.median(sorted_v)
    n = len(sorted_v)

    if n == 1:
        return med, med * 0.9, med * 1.1, med * 0.2
    elif n == 2:
        q1 = sorted_v[0]
        q3 = sorted_v[1]
    else:
        half = n // 2
        lower_half = sorted_v[:half]
        upper_half = sorted_v[half:] if n % 2 == 0 else sorted_v[half + 1:]
        q1 = statistics.median(lower_half)
        q3 = statistics.median(upper_half)

    iqr = max(q3 - q1, med * 0.08)
    return med, q1, q3, iqr


class FairPriceEngine:
    """
    Statistical Fair Price Engine.
    Uses market median and IQR spreads by model and grade to classify deals.
    Zero external paid APIs needed — fast, local, transparent statistical evaluation.
    """

    @classmethod
    def evaluate(
        cls,
        model_key: str,
        grade: str,
        asking_price: float,
        db: Session,
    ) -> PriceEstimateResponse:
        grade_upper = grade.strip().upper()
        if grade_upper not in ["A", "B", "C", "D"]:
            raise ValueError(f"Invalid condition grade: '{grade}'. Must be A, B, C, or D.")

        norm_query = normalize_model_key(model_key)

        all_model_rows = db.query(PriceComparable).all()
        matching_rows = [
            r for r in all_model_rows
            if norm_query in normalize_model_key(r.model_key) or normalize_model_key(r.model_key) in norm_query
        ]

        grade_matching_prices = [r.price for r in matching_rows if r.grade.upper() == grade_upper]
        grade_multipliers = {"A": 1.0, "B": 0.85, "C": 0.70, "D": 0.55}

        sample_size = len(grade_matching_prices)
        confidence = 0.5

        if sample_size >= 3:
            median_val, q1, q3, iqr = calculate_quartiles(grade_matching_prices)
            confidence = min(0.98, round(0.70 + (sample_size / 20.0) * 0.25, 2))
        elif matching_rows:
            all_prices = [r.price for r in matching_rows]
            base_median = statistics.median(all_prices)
            target_multiplier = grade_multipliers.get(grade_upper, 0.85)
            synthetic_prices = [p * (target_multiplier / 0.85) for p in all_prices]
            median_val, q1, q3, iqr = calculate_quartiles(synthetic_prices)
            sample_size = len(matching_rows)
            confidence = 0.65
        else:
            median_val = asking_price
            iqr = median_val * 0.12
            q1 = median_val - iqr / 2
            q3 = median_val + iqr / 2
            sample_size = 1
            confidence = 0.35

        fair_range_min = round(max(1.0, median_val - 0.65 * iqr), 2)
        fair_range_max = round(median_val + 0.65 * iqr, 2)

        diff_from_median = round(asking_price - median_val, 2)
        percentage_vs_median = round((diff_from_median / median_val) * 100, 1)

        if asking_price < fair_range_min:
            verdict = "Great deal"
        elif asking_price > fair_range_max:
            verdict = "Overpriced"
        else:
            verdict = "Fair"

        if verdict == "Great deal":
            savings = round(median_val - asking_price, 2)
            pct = abs(percentage_vs_median)
            explanation = (
                f"Asking price of ${asking_price:.2f} is ${savings:.2f} ({pct}%) below the market median "
                f"of ${median_val:.2f} for Grade {grade_upper} condition. Highly recommended purchase."
            )
        elif verdict == "Overpriced":
            premium = round(asking_price - median_val, 2)
            pct = percentage_vs_median
            explanation = (
                f"Asking price of ${asking_price:.2f} is ${premium:.2f} ({pct}%) above the market median "
                f"of ${median_val:.2f} for Grade {grade_upper}. Consider negotiating down towards the ${fair_range_max:.2f} range."
            )
        else:
            explanation = (
                f"Asking price of ${asking_price:.2f} aligns closely with the fair market range "
                f"(${fair_range_min:.2f} - ${fair_range_max:.2f}) for Grade {grade_upper} (market median: ${median_val:.2f})."
            )

        benchmarks: List[GradeBenchmark] = []
        for g in ["A", "B", "C", "D"]:
            g_prices = [r.price for r in matching_rows if r.grade.upper() == g]
            if g_prices:
                g_med = round(statistics.median(g_prices), 2)
                g_min = round(min(g_prices), 2)
                g_max = round(max(g_prices), 2)
                g_count = len(g_prices)
            else:
                multiplier_ratio = grade_multipliers[g] / grade_multipliers.get(grade_upper, 0.85)
                g_med = round(median_val * multiplier_ratio, 2)
                g_min = round(g_med * 0.90, 2)
                g_max = round(g_med * 1.10, 2)
                g_count = 0

            benchmarks.append(
                GradeBenchmark(
                    grade=g,
                    median_price=g_med,
                    min_price=g_min,
                    max_price=g_max,
                    sample_size=g_count,
                )
            )

        return PriceEstimateResponse(
            model_key=model_key,
            grade=grade_upper,
            asking_price=round(asking_price, 2),
            verdict=verdict,
            market_median=round(median_val, 2),
            fair_range_min=fair_range_min,
            fair_range_max=fair_range_max,
            iqr=round(iqr, 2),
            sample_size=sample_size,
            confidence=confidence,
            diff_from_median=diff_from_median,
            percentage_vs_median=percentage_vs_median,
            explanation=explanation,
            grade_benchmarks=benchmarks,
        )
