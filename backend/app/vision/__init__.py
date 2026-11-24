"""
Vision Feature Module:
- Perceptual Hashing (dHash) & Duplicate Photo Detection
- Local Computer Vision Defect Detection (Scratches, Cracks, Dents with Severity & Location)
- Condition Report Integration
"""

from .router import router
from .schemas import (
    BoundingBox,
    DefectItem,
    DuplicateCheckResponse,
    ImageAnalysisResult,
    ListingVisionReport,
)
from .service import (
    DefectDetectionEngine,
    VisionService,
    calculate_hash_similarity,
    check_duplicate_in_db,
    compute_dhash,
    hamming_distance,
)

__all__ = [
    "router",
    "VisionService",
    "DefectDetectionEngine",
    "compute_dhash",
    "hamming_distance",
    "calculate_hash_similarity",
    "check_duplicate_in_db",
    "BoundingBox",
    "DefectItem",
    "DuplicateCheckResponse",
    "ImageAnalysisResult",
    "ListingVisionReport",
]
