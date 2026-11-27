"""Cart: each resale item is unique, so a cart holds listings, not quantities."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user
from ..models import CartItem, Listing, User
from ..schemas_market import CartAdd, CartItemOut, CartOut

router = APIRouter(prefix="/cart", tags=["cart"])


def _cart(db: Session, user: User) -> CartOut:
    rows = (db.query(CartItem, Listing)
              .join(Listing, Listing.id == CartItem.listing_id)
              .filter(CartItem.user_id == user.id)
              .order_by(CartItem.id)
              .all())
    items = [CartItemOut(listing_id=l.id, title=l.title, price=l.price,
                         seller_id=l.seller_id, added_at=c.added_at) for c, l in rows]
    return CartOut(items=items, total=round(sum(i.price for i in items), 2))


@router.get("", response_model=CartOut)
def get_cart(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _cart(db, user)


@router.post("", response_model=CartOut, status_code=201)
def add_to_cart(data: CartAdd, db: Session = Depends(get_db),
                user: User = Depends(get_current_user)):
    listing = db.get(Listing, data.listing_id)
    if not listing:
        raise HTTPException(404, "Listing not found")
    if listing.status != "active":
        raise HTTPException(400, "This item is not available")
    if listing.seller_id == user.id:
        raise HTTPException(400, "You cannot buy your own listing")
    exists = db.query(CartItem).filter_by(user_id=user.id, listing_id=listing.id).first()
    if not exists:
        db.add(CartItem(user_id=user.id, listing_id=listing.id))
        db.commit()
    return _cart(db, user)


@router.delete("/{listing_id}", response_model=CartOut)
def remove_from_cart(listing_id: int, db: Session = Depends(get_db),
                     user: User = Depends(get_current_user)):
    item = db.query(CartItem).filter_by(user_id=user.id, listing_id=listing_id).first()
    if not item:
        raise HTTPException(404, "Item is not in your cart")
    db.delete(item)
    db.commit()
    return _cart(db, user)
