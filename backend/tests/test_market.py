"""Mon 23: cart, orders + Razorpay (mock mode), reviews, messages, admin."""
import hashlib
import hmac
import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ.pop("RAZORPAY_KEY_ID", None)
os.environ.pop("RAZORPAY_KEY_SECRET", None)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import User  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def tables():
    # other test files drop all tables when they finish, so make sure ours exist
    Base.metadata.create_all(bind=engine)
    yield


def _login(email, role):
    client.post("/auth/register", json={"name": email.split("@")[0], "email": email,
                                        "password": "secret1", "role": role})
    r = client.post("/auth/login", data={"username": email, "password": "secret1"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def _make_admin(email):
    db = SessionLocal()
    u = db.query(User).filter_by(email=email).first()
    u.role = "admin"
    db.commit()
    db.close()


def _new_listing(h, title, price, status=None):
    r = client.post("/listings", json={"category": "phones", "title": title, "price": price}, headers=h)
    return r.json()["id"]


def test_marketplace_flow():
    seller = _login("m_seller@x.com", "seller")
    buyer = _login("m_buyer@x.com", "buyer")
    other = _login("m_other@x.com", "buyer")
    phone = _new_listing(seller, "Pixel 6", 15000)
    laptop = _new_listing(seller, "ThinkPad", 30000.5)

    # cart
    assert client.post("/cart", json={"listing_id": phone}, headers=seller).status_code == 400
    assert client.post("/cart", json={"listing_id": phone}, headers=buyer).status_code == 201
    client.post("/cart", json={"listing_id": laptop}, headers=buyer)
    client.post("/cart", json={"listing_id": laptop}, headers=buyer)          # no duplicates
    cart = client.get("/cart", headers=buyer).json()
    assert len(cart["items"]) == 2 and cart["total"] == 45000.5
    client.post("/cart", json={"listing_id": phone}, headers=other)

    # checkout + payment (mock mode)
    co = client.post("/orders/checkout", headers=buyer).json()
    assert co["mock"] and co["amount"] == 4500050 and len(co["order_ids"]) == 2
    bad = {"razorpay_order_id": co["razorpay_order_id"], "razorpay_payment_id": "p",
           "razorpay_signature": "wrong"}
    assert client.post("/orders/verify", json=bad, headers=buyer).status_code == 400
    ok = dict(bad, razorpay_signature="mock_signature")
    paid = client.post("/orders/verify", json=ok, headers=buyer).json()
    assert all(o["status"] == "paid" for o in paid)
    assert client.get(f"/listings/{phone}").json()["status"] == "sold"
    assert client.get("/cart", headers=other).json()["items"] == []

    # status flow + review
    oid = paid[0]["id"]
    assert client.patch(f"/orders/{oid}/status", json={"status": "shipped"}, headers=buyer).status_code == 403
    assert client.patch(f"/orders/{oid}/status", json={"status": "shipped"}, headers=seller).status_code == 200
    assert client.post("/reviews", json={"order_id": oid, "rating": 5}, headers=buyer).status_code == 400
    client.patch(f"/orders/{oid}/status", json={"status": "delivered"}, headers=buyer)
    assert client.post("/reviews", json={"order_id": oid, "rating": 4, "text": "Good"}, headers=buyer).status_code == 201
    assert client.post("/reviews", json={"order_id": oid, "rating": 4}, headers=buyer).status_code == 400
    seller_id = paid[0]["seller_id"]
    assert client.get(f"/reviews/seller/{seller_id}").json()["average_rating"] == 4
    assert len(client.get("/orders/sales", headers=seller).json()) == 2

    # messages
    item = _new_listing(seller, "Headphones", 2000)
    assert client.post(f"/chats/{item}/messages", json={"body": "Still available?"}, headers=other).status_code == 201
    convo = client.get("/chats", headers=seller).json()[0]
    assert convo["unread"] == 1
    reply = {"body": "Yes!", "receiver_id": convo["other_user_id"]}
    assert client.post(f"/chats/{item}/messages", json=reply, headers=seller).status_code == 201
    assert len(client.get(f"/chats/{item}/messages", headers=other).json()) == 2

    # admin
    admin = _login("m_admin@x.com", "buyer")
    _make_admin("m_admin@x.com")
    assert client.get("/admin/stats", headers=buyer).status_code == 403
    assert client.get("/admin/stats", headers=admin).json()["orders_paid"] >= 2
    assert client.patch(f"/admin/listings/{item}", json={"status": "review"}, headers=admin).json()["status"] == "review"
    assert item in [l["id"] for l in client.get("/admin/review-queue", headers=admin).json()]
    assert client.patch(f"/admin/users/{seller_id}", json={"role": "banned"}, headers=admin).json()["role"] == "banned"
    assert client.get("/cart", headers=seller).status_code == 403             # banned user is locked out


def test_razorpay_signature_check(monkeypatch):
    from app import razorpay_service as r
    monkeypatch.setenv("RAZORPAY_KEY_ID", "rzp_test_x")
    monkeypatch.setenv("RAZORPAY_KEY_SECRET", "sek")
    sig = hmac.new(b"sek", b"order_1|pay_1", hashlib.sha256).hexdigest()
    assert r.verify_signature("order_1", "pay_1", sig)
    assert not r.verify_signature("order_1", "pay_1", "fake")
