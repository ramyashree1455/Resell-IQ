"""All tables from section 9 of the project report.
Shared by both teammates: change this file only after telling each other."""
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Float, Text, DateTime,
                        ForeignKey, JSON, Boolean, UniqueConstraint)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(10), default="buyer")  # buyer | seller | admin | banned
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Listing(Base):
    __tablename__ = "listings"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String(50), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, nullable=False)
    location = Column(String(100), default="")
    grade = Column(String(1), nullable=True)        # A-D, set by grading engine
    grade_score = Column(Integer, nullable=True)    # 0-100
    status = Column(String(15), default="active")   # active | sold | removed | review
    created_at = Column(DateTime, default=datetime.utcnow)

    seller = relationship("User")
    images = relationship("ListingImage", cascade="all, delete-orphan")


class ConditionReport(Base):
    __tablename__ = "condition_reports"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), unique=True)
    score = Column(Integer)
    grade = Column(String(1))
    defects_json = Column(JSON, default=list)
    confidence = Column(Float)
    interview_transcript = Column(Text, default="")


class ListingImage(Base):
    __tablename__ = "listing_images"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    url = Column(String(500), nullable=False)
    view_type = Column(String(30), default="front")
    analysis_json = Column(JSON, nullable=True)


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "listing_id", name="uq_cart_user_listing"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    added_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    amount = Column(Float)
    status = Column(String(15), default="placed")  # placed|paid|shipped|delivered|cancelled
    razorpay_order_id = Column(String(64), index=True, nullable=True)
    razorpay_payment_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    seller_id = Column(Integer, ForeignKey("users.id"), index=True)
    rating = Column(Integer)
    text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PriceComparable(Base):
    __tablename__ = "price_comparables"
    id = Column(Integer, primary_key=True)
    model_key = Column(String(150), index=True)
    grade = Column(String(1))
    price = Column(Float)
    sold_at = Column(DateTime, default=datetime.utcnow)
