import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _login(email, role):
    client.post("/auth/register", json={"name": "T", "email": email, "password": "secret1", "role": role})
    r = client.post("/auth/login", data={"username": email, "password": "secret1"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_full_listing_flow():
    h = _login("seller@x.com", "seller")
    r = client.post("/listings", json={"category": "phones", "title": "iPhone 12", "price": 25000,
                                       "location": "Mangalore"}, headers=h)
    assert r.status_code == 201
    lid = r.json()["id"]
    assert client.get("/listings", params={"q": "iphone", "max_price": 30000}).json()[0]["id"] == lid
    assert client.put(f"/listings/{lid}", json={"price": 22000}, headers=h).json()["price"] == 22000
    buyer = _login("buyer@x.com", "buyer")
    assert client.delete(f"/listings/{lid}", headers=buyer).status_code == 403
    assert client.delete(f"/listings/{lid}", headers=h).status_code == 204
    assert client.get(f"/listings/{lid}").status_code == 404


def test_buyer_cannot_create_listing():
    h = _login("b2@x.com", "buyer")
    r = client.post("/listings", json={"category": "x", "title": "y", "price": 1}, headers=h)
    assert r.status_code == 403
