import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models  # noqa: F401  (registers tables)
from .routers import auth, listings, interview

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ReSellIQ API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(interview.router)
# Next routers get added here, one line each:
#   Ramya : cart, orders, reviews, messages, admin
#   Friend: price


@app.get("/", tags=["health"])
def health():
    return {"app": "ReSellIQ", "status": "ok"}
