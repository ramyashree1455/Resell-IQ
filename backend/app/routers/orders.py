"""Checkout with Razorpay (test mode), payment verification and order status."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import razorpay_service as rzp
from ..database import get_db
from ..deps import get_current_user
from ..models import CartItem, Listing, Order, User
from ..schemas_market import (CheckoutOut, OrderOut, OrderStatusUpdate,
                                  PaymentVerify)

router = APIRouter(prefix="/orders", tags=["orders"])

# who may move an order from one status to the next
TRANSITIONS = {
    ("paid", "shipped"): "seller",
    ("shipped", "delivered"): "buyer",
    ("placed", "cancelled"): "buyer",
}


@router.post("/checkout", response_model=CheckoutOut)
def checkout(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Turn the cart into orders and one Razorpay order for the total."""
    rows = (db.query(CartItem, Listing)
              .join(Listing, Listing.id == CartItem.listing_id)
              .filter(CartItem.user_id == user.id).all())
    if not rows:
        raise HTTPException(400, "Your cart is empty")

    listings = [l for _, l in rows]
    for l in listings:
        if l.status != "active":
            raise HTTPException(400, f"'{l.title}' is no longer available; remove it from your cart")
        if l.seller_id == user.id:
            raise HTTPException(400, "You cannot buy your own listing")

    # drop this buyer's earlier unpaid attempts for the same items
    (db.query(Order)
       .filter(Order.buyer_id == user.id, Order.status == "placed",
               Order.listing_id.in_([l.id for l in listings]))
       .delete(synchronize_session=False))

    total = round(sum(l.price for l in listings), 2)
    rzp_order = rzp.create_order(total, receipt=f"user{user.id}-{len(listings)}items")

    orders = [Order(buyer_id=user.id, seller_id=l.seller_id, listing_id=l.id,
                    amount=l.price, status="placed", razorpay_order_id=rzp_order["id"])
              for l in listings]
    db.add_all(orders)
    db.commit()

    return CheckoutOut(razorpay_order_id=rzp_order["id"], amount=rzp_order["amount"],
                       currency=rzp_order.get("currency", "INR"), key_id=rzp.public_key(),
                       mock=rzp.is_mock(), order_ids=[o.id for o in orders])


@router.post("/verify", response_model=list[OrderOut])
def verify_payment(data: PaymentVerify, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    """Called by the frontend after Razorpay Checkout succeeds."""
    orders = (db.query(Order)
                .filter(Order.razorpay_order_id == data.razorpay_order_id,
                        Order.buyer_id == user.id, Order.status == "placed").all())
    if not orders:
        raise HTTPException(404, "No pending orders for this payment")
    if not rzp.verify_signature(data.razorpay_order_id, data.razorpay_payment_id,
                                data.razorpay_signature):
        raise HTTPException(400, "Payment signature is invalid")

    listing_ids = [o.listing_id for o in orders]
    for o in orders:
        o.status = "paid"
        o.razorpay_payment_id = data.razorpay_payment_id
    for l in db.query(Listing).filter(Listing.id.in_(listing_ids)):
        l.status = "sold"
    # sold items leave every cart, not just the buyer's
    db.query(CartItem).filter(CartItem.listing_id.in_(listing_ids)).delete(synchronize_session=False)
    db.commit()
    return orders


@router.get("", response_model=list[OrderOut])
def my_orders(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Order).filter(Order.buyer_id == user.id).order_by(Order.id.desc()).all()


@router.get("/sales", response_model=list[OrderOut])
def my_sales(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (db.query(Order)
              .filter(Order.seller_id == user.id, Order.status != "placed")
              .order_by(Order.id.desc()).all())


@router.patch("/{order_id}/status", response_model=OrderOut)
def update_status(order_id: int, data: OrderStatusUpdate, db: Session = Depends(get_db),
                  user: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if not order or user.id not in (order.buyer_id, order.seller_id):
        raise HTTPException(404, "Order not found")
    who = TRANSITIONS.get((order.status, data.status))
    if not who:
        raise HTTPException(400, f"Cannot change an order from '{order.status}' to '{data.status}'")
    allowed_id = order.seller_id if who == "seller" else order.buyer_id
    if user.id != allowed_id:
        raise HTTPException(403, f"Only the {who} can do this")
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order
