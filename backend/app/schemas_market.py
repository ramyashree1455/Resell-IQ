"""Request/response shapes for Ramya's marketplace routers (cart, orders, reviews, messages, admin).
Kept separate from schemas.py so we don't edit the same file."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- cart ----------
class CartAdd(BaseModel):
    listing_id: int


class CartItemOut(ORM):
    listing_id: int
    title: str
    price: float
    seller_id: int
    added_at: Optional[datetime] = None


class CartOut(BaseModel):
    items: list[CartItemOut]
    total: float


# ---------- orders / payments ----------
class CheckoutOut(BaseModel):
    razorpay_order_id: str
    amount: int                 # paise, what Razorpay Checkout expects
    currency: str
    key_id: str                 # public key for the frontend; "mock" in mock mode
    mock: bool
    order_ids: list[int]


class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class OrderOut(ORM):
    id: int
    buyer_id: int
    seller_id: Optional[int] = None
    listing_id: int
    amount: float
    status: str
    razorpay_order_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    created_at: Optional[datetime] = None


class OrderStatusUpdate(BaseModel):
    status: Literal["shipped", "delivered", "cancelled"]


# ---------- reviews ----------
class ReviewCreate(BaseModel):
    order_id: int
    rating: int = Field(ge=1, le=5)
    text: str = Field(default="", max_length=2000)


class ReviewOut(ORM):
    id: int
    order_id: int
    reviewer_id: Optional[int] = None
    seller_id: Optional[int] = None
    rating: int
    text: Optional[str] = ""
    created_at: Optional[datetime] = None


class SellerReviews(BaseModel):
    seller_id: int
    average_rating: Optional[float]
    count: int
    reviews: list[ReviewOut]


# ---------- chat ----------
class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    receiver_id: Optional[int] = None   # required only when the seller replies


class MessageOut(ORM):
    id: int
    listing_id: int
    sender_id: int
    receiver_id: int
    body: str
    is_read: Optional[bool] = False
    created_at: Optional[datetime] = None


class ConversationOut(BaseModel):
    listing_id: int
    other_user_id: int
    last_message: str
    last_at: Optional[datetime]
    unread: int


# ---------- admin ----------
class AdminListingUpdate(BaseModel):
    status: Literal["active", "review", "removed"]


class AdminUserUpdate(BaseModel):
    role: Literal["buyer", "seller", "admin", "banned"]
