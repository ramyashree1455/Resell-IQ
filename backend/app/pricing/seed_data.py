"""
Seed data script for realistic market price comparables (PriceComparable table).
Provides 180+ historical benchmark sales across smartphones, laptops, tablets,
audio gear, cameras, gaming consoles, and smartwatches.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session

from ..models import PriceComparable


SEED_DATA: List[Tuple[str, str, float, int]] = [
    # ==================== SMARTPHONES ====================
    # --- Apple iPhone 12 (64GB/128GB) ---
    ("iPhone 12", "A", 360.0, 3),
    ("iPhone 12", "A", 350.0, 9),
    ("iPhone 12", "B", 300.0, 5),
    ("iPhone 12", "B", 290.0, 14),
    ("iPhone 12", "C", 240.0, 8),
    ("iPhone 12", "D", 180.0, 19),

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
    ("iPhone 15", "A", 705.0, 9),
    ("iPhone 15", "B", 630.0, 3),
    ("iPhone 15", "B", 615.0, 12),
    ("iPhone 15", "C", 540.0, 16),
    ("iPhone 15", "D", 440.0, 22),

    # --- Apple iPhone 15 Pro (128GB) ---
    ("iPhone 15 Pro", "A", 980.0, 2),
    ("iPhone 15 Pro", "A", 960.0, 7),
    ("iPhone 15 Pro", "B", 860.0, 4),
    ("iPhone 15 Pro", "B", 840.0, 11),
    ("iPhone 15 Pro", "C", 720.0, 15),
    ("iPhone 15 Pro", "D", 580.0, 24),

    # --- Samsung Galaxy S22 ---
    ("Samsung Galaxy S22", "A", 380.0, 3),
    ("Samsung Galaxy S22", "A", 370.0, 10),
    ("Samsung Galaxy S22", "B", 320.0, 6),
    ("Samsung Galaxy S22", "B", 310.0, 15),
    ("Samsung Galaxy S22", "C", 260.0, 12),
    ("Samsung Galaxy S22", "D", 195.0, 21),

    # --- Samsung Galaxy S23 ---
    ("Samsung Galaxy S23", "A", 530.0, 3),
    ("Samsung Galaxy S23", "A", 520.0, 9),
    ("Samsung Galaxy S23", "A", 515.0, 12),
    ("Samsung Galaxy S23", "B", 455.0, 5),
    ("Samsung Galaxy S23", "B", 440.0, 14),
    ("Samsung Galaxy S23", "C", 380.0, 8),
    ("Samsung Galaxy S23", "D", 300.0, 22),

    # --- Samsung Galaxy S24 ---
    ("Samsung Galaxy S24", "A", 680.0, 2),
    ("Samsung Galaxy S24", "A", 665.0, 8),
    ("Samsung Galaxy S24", "B", 590.0, 5),
    ("Samsung Galaxy S24", "B", 575.0, 13),
    ("Samsung Galaxy S24", "C", 495.0, 16),
    ("Samsung Galaxy S24", "D", 390.0, 25),

    # --- OnePlus 11 5G ---
    ("OnePlus 11", "A", 410.0, 3),
    ("OnePlus 11", "A", 395.0, 8),
    ("OnePlus 11", "B", 350.0, 5),
    ("OnePlus 11", "B", 340.0, 14),
    ("OnePlus 11", "C", 285.0, 11),
    ("OnePlus 11", "D", 220.0, 20),

    # --- OnePlus 12 ---
    ("OnePlus 12", "A", 560.0, 2),
    ("OnePlus 12", "A", 545.0, 7),
    ("OnePlus 12", "B", 480.0, 5),
    ("OnePlus 12", "C", 400.0, 13),
    ("OnePlus 12", "D", 310.0, 22),

    # --- Google Pixel 7 ---
    ("Google Pixel 7", "A", 360.0, 4),
    ("Google Pixel 7", "A", 350.0, 9),
    ("Google Pixel 7", "B", 310.0, 7),
    ("Google Pixel 7", "B", 295.0, 16),
    ("Google Pixel 7", "C", 250.0, 12),
    ("Google Pixel 7", "D", 190.0, 28),

    # --- Google Pixel 8 ---
    ("Google Pixel 8", "A", 520.0, 3),
    ("Google Pixel 8", "A", 505.0, 10),
    ("Google Pixel 8", "B", 440.0, 6),
    ("Google Pixel 8", "C", 365.0, 14),
    ("Google Pixel 8", "D", 280.0, 23),

    # --- Nothing Phone 2 ---
    ("Nothing Phone 2", "A", 340.0, 4),
    ("Nothing Phone 2", "A", 330.0, 11),
    ("Nothing Phone 2", "B", 285.0, 7),
    ("Nothing Phone 2", "C", 235.0, 16),
    ("Nothing Phone 2", "D", 175.0, 24),

    # --- Redmi Note 13 Pro ---
    ("Redmi Note 13 Pro", "A", 230.0, 2),
    ("Redmi Note 13 Pro", "A", 220.0, 8),
    ("Redmi Note 13 Pro", "B", 190.0, 5),
    ("Redmi Note 13 Pro", "C", 155.0, 12),
    ("Redmi Note 13 Pro", "D", 115.0, 21),

    # ==================== LAPTOPS ====================
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
    ("MacBook Air M2", "A", 845.0, 14),
    ("MacBook Air M2", "B", 740.0, 5),
    ("MacBook Air M2", "B", 725.0, 14),
    ("MacBook Air M2", "C", 640.0, 11),
    ("MacBook Air M2", "D", 520.0, 24),

    # --- Apple MacBook Air M3 ---
    ("MacBook Air M3", "A", 1040.0, 2),
    ("MacBook Air M3", "A", 1015.0, 9),
    ("MacBook Air M3", "B", 900.0, 6),
    ("MacBook Air M3", "C", 770.0, 15),
    ("MacBook Air M3", "D", 620.0, 23),

    # --- Dell XPS 13 ---
    ("Dell XPS 13", "A", 720.0, 4),
    ("Dell XPS 13", "A", 700.0, 12),
    ("Dell XPS 13", "B", 610.0, 6),
    ("Dell XPS 13", "B", 595.0, 18),
    ("Dell XPS 13", "C", 510.0, 13),
    ("Dell XPS 13", "D", 400.0, 27),

    # --- Lenovo ThinkPad X1 ---
    ("Lenovo ThinkPad X1", "A", 640.0, 3),
    ("Lenovo ThinkPad X1", "A", 625.0, 11),
    ("Lenovo ThinkPad X1", "B", 545.0, 7),
    ("Lenovo ThinkPad X1", "C", 455.0, 14),
    ("Lenovo ThinkPad X1", "D", 350.0, 22),

    # --- Asus ROG Zephyrus G14 ---
    ("Asus ROG Zephyrus G14", "A", 780.0, 3),
    ("Asus ROG Zephyrus G14", "A", 760.0, 9),
    ("Asus ROG Zephyrus G14", "B", 665.0, 6),
    ("Asus ROG Zephyrus G14", "C", 550.0, 15),
    ("Asus ROG Zephyrus G14", "D", 430.0, 25),

    # ==================== TABLETS ====================
    # --- Apple iPad 10th Gen ---
    ("iPad 10th Gen", "A", 330.0, 3),
    ("iPad 10th Gen", "A", 320.0, 9),
    ("iPad 10th Gen", "B", 275.0, 7),
    ("iPad 10th Gen", "C", 225.0, 14),
    ("iPad 10th Gen", "D", 170.0, 25),

    # --- Apple iPad Air 5th Gen ---
    ("iPad Air 5th Gen", "A", 430.0, 2),
    ("iPad Air 5th Gen", "A", 415.0, 8),
    ("iPad Air 5th Gen", "B", 365.0, 5),
    ("iPad Air 5th Gen", "C", 300.0, 13),
    ("iPad Air 5th Gen", "D", 230.0, 22),

    # --- Samsung Galaxy Tab S9 ---
    ("Samsung Galaxy Tab S9", "A", 540.0, 3),
    ("Samsung Galaxy Tab S9", "A", 525.0, 10),
    ("Samsung Galaxy Tab S9", "B", 460.0, 6),
    ("Samsung Galaxy Tab S9", "C", 385.0, 14),
    ("Samsung Galaxy Tab S9", "D", 295.0, 24),

    # ==================== AUDIO ====================
    # --- Sony WH-1000XM4 Headphones ---
    ("Sony WH-1000XM4", "A", 220.0, 2),
    ("Sony WH-1000XM4", "A", 215.0, 8),
    ("Sony WH-1000XM4", "A", 210.0, 11),
    ("Sony WH-1000XM4", "B", 180.0, 5),
    ("Sony WH-1000XM4", "B", 175.0, 15),
    ("Sony WH-1000XM4", "C", 140.0, 10),
    ("Sony WH-1000XM4", "D", 100.0, 26),

    # --- Sony WH-1000XM5 ---
    ("Sony WH-1000XM5", "A", 290.0, 2),
    ("Sony WH-1000XM5", "A", 280.0, 7),
    ("Sony WH-1000XM5", "B", 240.0, 5),
    ("Sony WH-1000XM5", "C", 195.0, 14),
    ("Sony WH-1000XM5", "D", 145.0, 22),

    # --- Apple AirPods Pro 2 ---
    ("AirPods Pro 2", "A", 185.0, 1),
    ("AirPods Pro 2", "A", 175.0, 6),
    ("AirPods Pro 2", "A", 180.0, 10),
    ("AirPods Pro 2", "B", 150.0, 4),
    ("AirPods Pro 2", "B", 145.0, 13),
    ("AirPods Pro 2", "C", 120.0, 11),
    ("AirPods Pro 2", "D", 85.0, 21),

    # --- Bose QuietComfort 45 ---
    ("Bose QuietComfort 45", "A", 205.0, 3),
    ("Bose QuietComfort 45", "B", 170.0, 7),
    ("Bose QuietComfort 45", "C", 135.0, 15),
    ("Bose QuietComfort 45", "D", 95.0, 24),

    # ==================== CAMERAS ====================
    # --- Sony Alpha a7 III ---
    ("Sony Alpha a7 III", "A", 1060.0, 3),
    ("Sony Alpha a7 III", "A", 1040.0, 11),
    ("Sony Alpha a7 III", "B", 910.0, 6),
    ("Sony Alpha a7 III", "C", 760.0, 14),
    ("Sony Alpha a7 III", "D", 590.0, 26),

    # --- Canon EOS R6 ---
    ("Canon EOS R6", "A", 1160.0, 2),
    ("Canon EOS R6", "B", 990.0, 8),
    ("Canon EOS R6", "C", 820.0, 16),
    ("Canon EOS R6", "D", 640.0, 25),

    # ==================== GAMING & WEARABLES ====================
    # --- PlayStation 5 ---
    ("PlayStation 5", "A", 470.0, 2),
    ("PlayStation 5", "A", 460.0, 8),
    ("PlayStation 5", "A", 475.0, 12),
    ("PlayStation 5", "B", 405.0, 5),
    ("PlayStation 5", "B", 395.0, 13),
    ("PlayStation 5", "C", 335.0, 11),
    ("PlayStation 5", "D", 260.0, 22),

    # --- Nintendo Switch OLED ---
    ("Nintendo Switch OLED", "A", 285.0, 3),
    ("Nintendo Switch OLED", "B", 240.0, 7),
    ("Nintendo Switch OLED", "C", 195.0, 14),
    ("Nintendo Switch OLED", "D", 145.0, 23),

    # --- Apple Watch Series 9 ---
    ("Apple Watch Series 9", "A", 330.0, 2),
    ("Apple Watch Series 9", "B", 280.0, 6),
    ("Apple Watch Series 9", "C", 230.0, 13),
    ("Apple Watch Series 9", "D", 175.0, 21),
]


def seed_market_comparables(db: Session, overwrite: bool = False) -> int:
    """
    Populates PriceComparable table with diverse multi-category resale market benchmarks.
    Idempotent: adds any missing models from SEED_DATA unless overwrite=True replaces all.
    """
    existing_count = db.query(PriceComparable).count()

    if overwrite and existing_count > 0:
        db.query(PriceComparable).delete()
        db.commit()
        existing_models = set()
    else:
        existing_models = {row[0] for row in db.query(PriceComparable.model_key).distinct().all()}

    now = datetime.utcnow()
    records = []
    for model_key, grade, price, days_ago in SEED_DATA:
        if model_key in existing_models:
            continue
        sold_time = now - timedelta(days=days_ago)
        records.append(
            PriceComparable(
                model_key=model_key,
                grade=grade,
                price=price,
                sold_at=sold_time,
            )
        )

    if records:
        db.add_all(records)
        db.commit()

    return len(records)
