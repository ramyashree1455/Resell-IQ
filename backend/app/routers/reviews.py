"""Buyers review sellers once per delivered order."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import Order, Review, User
from ..schemas_market import ReviewCreate, ReviewOut, SellerReviews

router = APIRouter(prefix="/reviews", tags=["reviews"])


def _refresh_seller_rating(db: Session, seller_id: int):
    """Keep users.rating equal to the seller's average review."""
    avg = db.query(func.avg(Review.rating)).filter(Review.seller_id == seller_id).scalar()
    seller = db.get(User, seller_id)
    if seller is not None and hasattr(seller, "rating"):
        seller.rating = round(float(avg), 2) if avg is not None else None


@router.post("", response_model=ReviewOut, status_code=201)
def create_review(data: ReviewCreate, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    order = db.get(Order, data.order_id)
    if not order or order.buyer_id != user.id:
        raise HTTPException(404, "Order not found")
    if order.status != "delivered":
        raise HTTPException(400, "You can review only after the order is delivered")
    if db.query(Review).filter_by(order_id=order.id).first():
        raise HTTPException(400, "You already reviewed this order")

    review = Review(order_id=order.id, reviewer_id=user.id, seller_id=order.seller_id,
                    rating=data.rating, text=data.text)
    db.add(review)
    db.flush()
    _refresh_seller_rating(db, order.seller_id)
    db.commit()
    db.refresh(review)
    return review


@router.get("/seller/{seller_id}", response_model=SellerReviews)
def seller_reviews(seller_id: int, db: Session = Depends(get_db)):
    reviews = (db.query(Review).filter(Review.seller_id == seller_id)
                 .order_by(Review.id.desc()).all())
    avg = round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else None
    return SellerReviews(seller_id=seller_id, average_rating=avg,
                         count=len(reviews), reviews=reviews)
