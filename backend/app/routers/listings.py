import os
import shutil
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, require_roles
from ..models import Listing, ListingImage, User
from ..schemas import ListingCreate, ListingUpdate, ListingOut, ImageOut

router = APIRouter(prefix="/listings", tags=["listings"])
UPLOAD_DIR = "uploads"


@router.post("", response_model=ListingOut, status_code=201)
def create_listing(data: ListingCreate, user: User = Depends(require_roles("seller", "admin")),
                   db: Session = Depends(get_db)):
    listing = Listing(seller_id=user.id, **data.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("", response_model=List[ListingOut])
def search_listings(
    q: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    grade: Optional[str] = Query(default=None, pattern="^[A-D]$"),
    location: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    """Search + filters (category, price, grade, location) from the report."""
    query = db.query(Listing).filter(Listing.status == "active")
    if q:
        query = query.filter(Listing.title.ilike(f"%{q}%"))
    if category:
        query = query.filter(Listing.category.ilike(category))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)
    if grade:
        query = query.filter(Listing.grade == grade)
    if location:
        query = query.filter(Listing.location.ilike(f"%{location}%"))
    return query.order_by(Listing.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = db.get(Listing, listing_id)
    if not listing or listing.status == "removed":
        raise HTTPException(404, "Listing not found")
    return listing


def _own_listing(listing_id: int, user: User, db: Session) -> Listing:
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.seller_id != user.id and user.role != "admin":
        raise HTTPException(403, "Not your listing")
    return listing


@router.put("/{listing_id}", response_model=ListingOut)
def update_listing(listing_id: int, data: ListingUpdate,
                   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    listing = _own_listing(listing_id, user, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


@router.delete("/{listing_id}", status_code=204)
def delete_listing(listing_id: int, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    listing = _own_listing(listing_id, user, db)
    db.delete(listing)
    db.commit()


@router.post("/{listing_id}/images", response_model=ImageOut, status_code=201)
def upload_image(listing_id: int, view_type: str = "front", file: UploadFile = File(...),
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Saves to local uploads/ for now. Swap for S3/Cloudinary later."""
    listing = _own_listing(listing_id, user, db)
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(400, "Only image files are allowed")
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(UPLOAD_DIR, name), "wb") as out:
        shutil.copyfileobj(file.file, out)
    img = ListingImage(listing_id=listing.id, url=f"/uploads/{name}", view_type=view_type)
    db.add(img)
    db.commit()
    db.refresh(img)
    return img
