"""
Fair Price Engine:
Calculates statistical median and spread by model_key and condition grade (A, B, C, D).
Classifies asking price as 'Great deal', 'Fair', or 'Overpriced'.
Provides transparent market benchmarks and cross-grade price comparisons.
"""

import math
import re
import statistics
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models import PriceComparable
from .schemas import GradeBenchmark, PriceEstimateResponse


def normalize_model_key(raw_key: str) -> str:
    """Normalizes model keys (e.g., '  Apple iPhone13 128GB  ' -> 'iphone 13')."""
    cleaned = raw_key.strip().lower()
    prefixes = ["apple ", "samsung ", "google ", "dell ", "sony ", "lenovo "]
    for p in prefixes:
        if cleaned.startswith(p):
            cleaned = cleaned[len(p):].strip()

    # Split merged letters and numbers: 'iphone13' -> 'iphone 13'
    cleaned = re.sub(r'([a-zA-Z]+)(\d+)', r'\1 \2', cleaned)
    cleaned = re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', cleaned)

    # Strip storage specifications (e.g., '128gb', '256 gb', '64gb', '512gb', '1tb')
    cleaned = re.sub(r'\b\d+\s*(gb|tb|mb)\b', '', cleaned, flags=re.IGNORECASE)

    # Clean multiple spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
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
        currency: Optional[str] = None,
        mrp: Optional[float] = None,
    ) -> PriceEstimateResponse:
        grade_upper = grade.strip().upper()
        if grade_upper not in ["A", "B", "C", "D"]:
            raise ValueError(f"Invalid condition grade: '{grade}'. Must be A, B, C, or D.")

        # Auto-seed database if empty or missing newly added benchmark models
        from .seed_data import SEED_DATA, seed_market_comparables
        if db.query(PriceComparable).count() < len(SEED_DATA):
            seed_market_comparables(db)

        norm_query = normalize_model_key(model_key)
        query_words = set(norm_query.split())

        all_model_rows = db.query(PriceComparable).all()
        matching_rows = []
        for r in all_model_rows:
            db_norm = normalize_model_key(r.model_key)
            db_words = set(db_norm.split())
            if (norm_query in db_norm or db_norm in norm_query) or (db_words and db_words.issubset(query_words)):
                matching_rows.append(r)

        # Harmonize currency: detect INR if currency is INR or asking_price > 1000
        is_inr = (currency is not None and currency.upper() == "INR") or asking_price > 1000
        curr_mult = 83.0 if (is_inr and matching_rows and all(r.price < 2500 for r in matching_rows)) else 1.0
        curr_symbol = "₹" if is_inr else "$"

        grade_matching_prices = [r.price * curr_mult for r in matching_rows if r.grade.upper() == grade_upper]
        grade_multipliers = {"A": 1.0, "B": 0.85, "C": 0.70, "D": 0.55}

        sample_size = len(grade_matching_prices)
        confidence = 0.5

        if sample_size >= 3:
            median_val, q1, q3, iqr = calculate_quartiles(grade_matching_prices)
            confidence = min(0.98, round(0.70 + (sample_size / 20.0) * 0.25, 2))
        elif matching_rows:
            all_prices = [r.price * curr_mult for r in matching_rows]
            base_median = statistics.median(all_prices)
            target_multiplier = grade_multipliers.get(grade_upper, 0.85)
            synthetic_prices = [p * (target_multiplier / 0.85) for p in all_prices]
            median_val, q1, q3, iqr = calculate_quartiles(synthetic_prices)
            sample_size = len(matching_rows)
            confidence = 0.65
        else:
            # 1. If the listing's original retail M.R.P. is known (e.g. from Chrome Extension),
            #    compute genuine secondary-market depreciation benchmarks per condition grade.
            if mrp is not None and mrp > 0:
                resale_ratios = {"A": 0.78, "B": 0.65, "C": 0.50, "D": 0.35}
                median_val = round(mrp * resale_ratios.get(grade_upper, 0.65), 2)
                iqr = round(max(10.0, median_val * 0.14), 2)
                q1 = round(median_val - iqr / 2, 2)
                q3 = round(median_val + iqr / 2, 2)
                sample_size = 0
                confidence = 0.60
            else:
                # 2. Fixed category secondary-market baselines (never mirrors asking_price)
                is_phone = any(w in norm_query for w in ["phone", "iphone", "galaxy", "pixel", "oneplus", "smartphone", "mobile", "redmi", "realme", "vivo", "oppo", "xiaomi", "motorola", "nord", "iqoo", "poco", "nothing"])
                is_laptop = any(w in norm_query for w in ["macbook", "laptop", "thinkpad", "xps", "notebook", "rog", "pavilion", "ideapad", "legion", "vivobook", "computer", "desktop"])
                is_tablet = any(w in norm_query for w in ["ipad", "tablet", "tab"])
                is_audio = any(w in norm_query for w in ["headphone", "earphone", "earbud", "airpod", "buds", "wh-1000", "bose", "jbl", "sony", "audio", "speaker"])
                is_gaming = any(w in norm_query for w in ["playstation", "ps5", "ps4", "xbox", "nintendo", "switch", "console"])
                is_watch = any(w in norm_query for w in ["watch", "smartwatch", "fitbit", "garmin"])
                is_accessory = any(w in norm_query for w in ["case", "cover", "protector", "guard", "strap", "cable", "charger", "sleeve", "adapter", "stand", "holder", "mouse", "keyboard"])
                is_apparel = any(w in norm_query for w in ["tee", "tshirt", "shirt", "apparel", "clothing", "top", "baggy", "casual", "printed", "hoodie", "jacket", "pants", "jeans", "cotton", "wear", "armhole", "troopers", "monkey"])

                if is_apparel:
                    base_val = 899.0 if is_inr else 12.0
                elif is_accessory:
                    base_val = 1199.0 if is_inr else 15.0
                elif is_watch:
                    base_val = 18000.0 if is_inr else 220.0
                elif is_audio:
                    base_val = 12999.0 if is_inr else 150.0
                elif is_tablet:
                    base_val = 32000.0 if is_inr else 380.0
                elif is_gaming:
                    base_val = 36000.0 if is_inr else 420.0
                elif is_laptop:
                    base_val = 58000.0 if is_inr else 700.0
                elif is_phone:
                    base_val = 38000.0 if is_inr else 450.0
                else:
                    # Fixed baseline for unknown items so asking_price variations change the verdict
                    base_val = 15000.0 if is_inr else 180.0

                median_val = round(base_val * grade_multipliers.get(grade_upper, 0.85), 2)
                iqr = round(median_val * 0.16, 2)
                q1 = round(median_val - iqr / 2, 2)
                q3 = round(median_val + iqr / 2, 2)
                sample_size = 0
                confidence = 0.40

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
                f"Asking price of {curr_symbol}{asking_price:,.0f} is {curr_symbol}{savings:,.0f} ({pct}%) below the market median "
                f"of {curr_symbol}{median_val:,.0f} for Grade {grade_upper} condition. Highly recommended purchase."
            )
        elif verdict == "Overpriced":
            premium = round(asking_price - median_val, 2)
            pct = percentage_vs_median
            explanation = (
                f"Asking price of {curr_symbol}{asking_price:,.0f} is {curr_symbol}{premium:,.0f} ({pct}%) above the market median "
                f"of {curr_symbol}{median_val:,.0f} for Grade {grade_upper}. Consider negotiating down towards the {curr_symbol}{fair_range_max:,.0f} range."
            )
        else:
            explanation = (
                f"Asking price of {curr_symbol}{asking_price:,.0f} aligns closely with the fair market range "
                f"({curr_symbol}{fair_range_min:,.0f} - {curr_symbol}{fair_range_max:,.0f}) for Grade {grade_upper} (market median: {curr_symbol}{median_val:,.0f})."
            )

        benchmarks: List[GradeBenchmark] = []
        for g in ["A", "B", "C", "D"]:
            g_prices = [r.price * curr_mult for r in matching_rows if r.grade.upper() == g]
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
