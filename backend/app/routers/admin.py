"""Admin moderation: listings (incl. the low-confidence review queue), users, orders.

The friend's grading engine sets listing.status = "review" when confidence is low;
those listings show up in /admin/review-queue."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_roles
from ..models import Listing, Order, User
from ..schemas_market import AdminListingUpdate, AdminUserUpdate, OrderOut

router = APIRouter(prefix="/admin", tags=["admin"])


require_admin = require_roles("admin")


def _listing_dict(l: Listing) -> dict:
    return {"id": l.id, "title": l.title, "price": l.price, "status": l.status,
            "seller_id": l.seller_id, "category": getattr(l, "category", None),
            "grade": getattr(l, "grade", None)}


def _user_dict(u: User) -> dict:
    return {"id": u.id, "name": getattr(u, "name", None), "email": getattr(u, "email", None),
            "role": getattr(u, "role", None), "rating": getattr(u, "rating", None)}


@router.get("/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    paid = ("paid", "shipped", "delivered")
    return {
        "users": db.query(User).count(),
        "listings_active": db.query(Listing).filter(Listing.status == "active").count(),
        "listings_in_review": db.query(Listing).filter(Listing.status == "review").count(),
        "orders_paid": db.query(Order).filter(Order.status.in_(paid)).count(),
        "revenue": round(sum(o.amount for o in db.query(Order).filter(Order.status.in_(paid))), 2),
    }


@router.get("/listings")
def all_listings(status: Optional[str] = None, db: Session = Depends(get_db),
                 _: User = Depends(require_admin)):
    q = db.query(Listing)
    if status:
        q = q.filter(Listing.status == status)
    return [_listing_dict(l) for l in q.order_by(Listing.id.desc()).all()]


@router.get("/review-queue")
def review_queue(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """Listings whose AI grade had low confidence wait here for a human."""
    rows = db.query(Listing).filter(Listing.status == "review").order_by(Listing.id).all()
    return [_listing_dict(l) for l in rows]


@router.patch("/listings/{listing_id}")
def moderate_listing(listing_id: int, data: AdminListingUpdate, db: Session = Depends(get_db),
                     _: User = Depends(require_admin)):
    listing = db.get(Listing, listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.status == "sold":
        raise HTTPException(400, "Sold listings cannot be changed")
    listing.status = data.status
    db.commit()
    return _listing_dict(listing)


@router.get("/users")
def all_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return [_user_dict(u) for u in db.query(User).order_by(User.id).all()]


@router.patch("/users/{user_id}")
def moderate_user(user_id: int, data: AdminUserUpdate, db: Session = Depends(get_db),
                  admin: User = Depends(require_admin)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    if target.id == admin.id:
        raise HTTPException(400, "You cannot change your own role")
    target.role = data.role
    if data.role == "banned":            # hide a banned user's live listings
        for l in db.query(Listing).filter(Listing.seller_id == target.id,
                                          Listing.status == "active"):
            l.status = "removed"
    db.commit()
    return _user_dict(target)


@router.get("/orders", response_model=list[OrderOut])
def all_orders(status: Optional[str] = None, db: Session = Depends(get_db),
               _: User = Depends(require_admin)):
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    return q.order_by(Order.id.desc()).all()
