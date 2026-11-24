"""
Seed data script for realistic market price comparables (PriceComparable table).
Provides 60+ historical benchmark sales across smartphones, laptops, audio gear, and tablets.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from ..models import PriceComparable


SEED_DATA: List[Tuple[str, str, float, int]] = [
    # --- Apple iPhone 13 (128GB) ---
    ("iPhone 13", "A", 480.0, 3),
    ("iPhone 13", "A", 475.0, 7),
    ("iPhone 13", "A", 490.0, 14),
    ("iPhone 13", "B", 420.0, 2),
    ("iPhone 13", "B", 410.0, 5),
    ("iPhone 13", "B", 395.0, 12),
    ("iPhone 13", "B", 405.0, 18),
    ("iPhone 13", "C", 340.0, 4),
    ("iPhone 13", "C", 325.0, 9),
    ("iPhone 13", "C", 350.0, 21),
    ("iPhone 13", "D", 260.0, 10),
    ("iPhone 13", "D", 240.0, 25),

    # --- Apple iPhone 14 (128GB) ---
    ("iPhone 14", "A", 590.0, 2),
    ("iPhone 14", "A", 575.0, 6),
    ("iPhone 14", "A", 580.0, 15),
    ("iPhone 14", "B", 510.0, 4),
    ("iPhone 14", "B", 495.0, 11),
    ("iPhone 14", "B", 500.0, 20),
    ("iPhone 14", "C", 430.0, 8),
    ("iPhone 14", "C", 415.0, 19),
    ("iPhone 14", "D", 330.0, 14),

    # --- Apple iPhone 15 (128GB) ---
    ("iPhone 15", "A", 710.0, 1),
    ("iPhone 15", "A", 695.0, 5),
    ("iPhone 15", "B", 630.0, 3),
    ("iPhone 15", "B", 615.0, 12),
    ("iPhone 15", "C", 540.0, 16),
    ("iPhone 15", "D", 440.0, 22),

    # --- Apple MacBook Air M1 (256GB / 8GB) ---
    ("MacBook Air M1", "A", 650.0, 2),
    ("MacBook Air M1", "A", 640.0, 8),
    ("MacBook Air M1", "A", 660.0, 16),
    ("MacBook Air M1", "B", 560.0, 4),
    ("MacBook Air M1", "B", 545.0, 9),
    ("MacBook Air M1", "B", 575.0, 17),
    ("MacBook Air M1", "C", 470.0, 6),
    ("MacBook Air M1", "C", 450.0, 15),
    ("MacBook Air M1", "D", 370.0, 20),

    # --- Apple MacBook Air M2 ---
    ("MacBook Air M2", "A", 850.0, 3),
    ("MacBook Air M2", "A", 830.0, 10),
    ("MacBook Air M2", "B", 740.0, 5),
    ("MacBook Air M2", "B", 725.0, 14),
    ("MacBook Air M2", "C", 640.0, 11),
    ("MacBook Air M2", "D", 520.0, 24),

    # --- Dell XPS 13 ---
    ("Dell XPS 13", "A", 720.0, 4),
    ("Dell XPS 13", "A", 700.0, 12),
    ("Dell XPS 13", "B", 610.0, 6),
    ("Dell XPS 13", "B", 595.0, 18),
    ("Dell XPS 13", "C", 510.0, 13),
    ("Dell XPS 13", "D", 400.0, 27),

    # --- Samsung Galaxy S23 ---
    ("Samsung Galaxy S23", "A", 530.0, 3),
    ("Samsung Galaxy S23", "A", 520.0, 9),
    ("Samsung Galaxy S23", "B", 455.0, 5),
    ("Samsung Galaxy S23", "B", 440.0, 14),
    ("Samsung Galaxy S23", "C", 380.0, 8),
    ("Samsung Galaxy S23", "D", 300.0, 22),

    # --- Google Pixel 7 ---
    ("Google Pixel 7", "A", 360.0, 4),
    ("Google Pixel 7", "B", 310.0, 7),
    ("Google Pixel 7", "B", 295.0, 16),
    ("Google Pixel 7", "C", 250.0, 12),
    ("Google Pixel 7", "D", 190.0, 28),

    # --- Sony WH-1000XM4 Headphones ---
    ("Sony WH-1000XM4", "A", 220.0, 2),
    ("Sony WH-1000XM4", "A", 215.0, 8),
    ("Sony WH-1000XM4", "B", 180.0, 5),
    ("Sony WH-1000XM4", "B", 175.0, 15),
    ("Sony WH-1000XM4", "C", 140.0, 10),
    ("Sony WH-1000XM4", "D", 100.0, 26),

    # --- Apple AirPods Pro 2 ---
    ("AirPods Pro 2", "A", 185.0, 1),
    ("AirPods Pro 2", "A", 175.0, 6),
    ("AirPods Pro 2", "B", 150.0, 4),
    ("AirPods Pro 2", "B", 145.0, 13),
    ("AirPods Pro 2", "C", 120.0, 11),
    ("AirPods Pro 2", "D", 85.0, 21),

    # --- Apple iPad 10th Gen ---
    ("iPad 10th Gen", "A", 330.0, 3),
    ("iPad 10th Gen", "B", 275.0, 7),
    ("iPad 10th Gen", "C", 225.0, 14),
    ("iPad 10th Gen", "D", 170.0, 25),
]


def seed_market_comparables(db: Session, overwrite: bool = False) -> int:
    """
    Populates PriceComparable table with realistic baseline resale market data.
    Idempotent: skips if table is already populated unless overwrite=True.
    """
    existing_count = db.query(PriceComparable).count()
    if existing_count > 0 and not overwrite:
        return existing_count

    if overwrite and existing_count > 0:
        db.query(PriceComparable).delete()
        db.commit()

    now = datetime.utcnow()
    records = []
    for model_key, grade, price, days_ago in SEED_DATA:
        sold_time = now - timedelta(days=days_ago)
        records.append(
            PriceComparable(
                model_key=model_key,
                grade=grade,
                price=price,
                sold_at=sold_time,
            )
        )

    db.add_all(records)
    db.commit()
    return len(records)
