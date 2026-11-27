import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import cart, orders, reviews, messages, admin  # Ramya: marketplace
from .database import Base, engine
from . import models  # noqa: F401  (registers tables)
from .routers import auth, listings

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ReSellIQ API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(listings.router)
# Next routers get added here, one line each:
#   Ramya : cart, orders, reviews, messages, admin
#   Friend: interview, grading, price

app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(messages.router)
app.include_router(admin.router)


@app.get("/", tags=["health"])
def health():
    return {"app": "ReSellIQ", "status": "ok"}
