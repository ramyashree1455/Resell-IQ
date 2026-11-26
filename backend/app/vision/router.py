"""
Vision Feature Router.
"""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from .schemas import (
    DuplicateCheckResponse,
    ImageAnalysisResult,
    ListingVisionReport,
)
from .service import DefectDetectionEngine, VisionService

router = APIRouter(prefix="/vision", tags=["vision"])


@router.post("/analyze/{listing_id}", response_model=ListingVisionReport)
def analyze_listing_vision_endpoint(
    listing_id: int,
    db: Session = Depends(get_db),
):
    """
    Runs complete Computer Vision pipeline on all images of a listing:
    1. Computes perceptual dHash for duplicate & stolen photo detection.
    2. Identifies scratches, cracks, and dents with severity and location.
    3. Saves evidence into listing_images.analysis_json.
    4. Integrates defects into condition_reports.defects_json and updates condition grade.
    """
    try:
        report = VisionService.analyze_listing_images(listing_id=listing_id, db=db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual analysis failed: {str(e)}")


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate_endpoint(
    file: Optional[UploadFile] = File(None),
    image_hash: Optional[str] = Form(None),
    exclude_listing_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
):
    """
    Checks an uploaded image or perceptual hash against existing marketplace images
    to detect duplicate or stolen photos.
    """
    if file:
        content = file.file.read()
        return VisionService.check_duplicate(db=db, image_input=content, exclude_listing_id=exclude_listing_id)
    elif image_hash:
        return VisionService.check_duplicate(db=db, image_input=image_hash, exclude_listing_id=exclude_listing_id)
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded file or an image_hash")


@router.post("/detect-defects", response_model=ImageAnalysisResult)
def detect_defects_endpoint(
    file: UploadFile = File(...),
    view_type: str = Form("front"),
    product_category: Optional[str] = Form(None),
    product_title: Optional[str] = Form(None),
):
    """
    Directly inspects an uploaded image for physical defects (scratches, cracks, dents)
    and computes its perceptual hash. Validates that the image matches the selected product.
    """
    content = file.file.read()
    try:
        return DefectDetectionEngine.analyze_image(
            content,
            view_type=view_type,
            product_category=product_category,
            product_title=product_title,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image inspection failed: {str(e)}")
