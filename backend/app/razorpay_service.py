"""Razorpay test-mode payments.

Set RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET (test keys start with rzp_test_)
in .env. If either is missing, MOCK MODE is used so you can develop without
keys: orders get fake ids and the signature "mock_signature" is accepted.
"""
import hashlib
import hmac
import os
import uuid

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv not installed; rely on real env vars
    pass


def _keys():
    return os.getenv("RAZORPAY_KEY_ID", ""), os.getenv("RAZORPAY_KEY_SECRET", "")


def is_mock() -> bool:
    key_id, secret = _keys()
    return not (key_id and secret)


def public_key() -> str:
    return "mock" if is_mock() else _keys()[0]


def create_order(amount_rupees: float, receipt: str) -> dict:
    """Create a Razorpay order. Returns at least {'id', 'amount', 'currency'}."""
    paise = int(round(amount_rupees * 100))
    if is_mock():
        return {"id": f"order_mock_{uuid.uuid4().hex[:14]}", "amount": paise, "currency": "INR"}

    import razorpay  # pip install razorpay
    key_id, secret = _keys()
    client = razorpay.Client(auth=(key_id, secret))
    return client.order.create({
        "amount": paise,
        "currency": "INR",
        "receipt": receipt[:40],
        "payment_capture": 1,
    })


def verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Razorpay signs 'order_id|payment_id' with your secret (HMAC-SHA256)."""
    if is_mock():
        return signature == "mock_signature"
    _, secret = _keys()
    expected = hmac.new(secret.encode(), f"{order_id}|{payment_id}".encode(),
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
