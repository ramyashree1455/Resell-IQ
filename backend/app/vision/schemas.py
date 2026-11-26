"""
Vision Feature Pydantic Schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x: float = Field(..., description="Top-left X coordinate normalized 0.0 - 1.0")
    y: float = Field(..., description="Top-left Y coordinate normalized 0.0 - 1.0")
    width: float = Field(..., description="Width normalized 0.0 - 1.0")
    height: float = Field(..., description="Height normalized 0.0 - 1.0")


class DefectItem(BaseModel):
    type: str = Field(..., description="Defect type: scratch | crack | dent | blemish | discoloration")
    severity: str = Field(..., description="Severity level: minor | moderate | major")
    location: BoundingBox
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class ImageAnalysisResult(BaseModel):
    image_id: Optional[int] = None
    url: Optional[str] = None
    view_type: Optional[str] = "front"
    perceptual_hash: str
    is_valid_device_photo: bool = True
    validation_message: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of_image_id: Optional[int] = None
    duplicate_of_listing_id: Optional[int] = None
    similarity_score: float = 0.0
    defects: List[DefectItem] = []
    defect_count: int = 0
    overall_severity: str = "none"  # none | minor | moderate | major
    is_clean: bool = True
    summary: str = ""


class ListingVisionReport(BaseModel):
    listing_id: int
    total_images: int
    duplicate_images_detected: int
    total_defects_found: int
    images_analysis: List[ImageAnalysisResult]
    condition_report_updated: bool
    recommended_grade: Optional[str] = None
    recommended_score: Optional[int] = None
    score_penalty: int = 0
    warnings: List[str] = []


class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    similarity_score: float
    perceptual_hash: str
    matched_image_id: Optional[int] = None
    matched_listing_id: Optional[int] = None
    message: str
