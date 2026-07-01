"""
main.py
-------
FastAPI application entry point.

Wires together configuration, database, CORS, and the auth/users routers into a
single JSON REST API for user registration, login, and profile retrieval.

Run with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, users

# Create tables on startup for local/dev convenience. In production, prefer the
# Alembic migrations under ``alembic/`` and remove or guard this call.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Registration & Job Profile API",
    description=(
        "Register users with job profile data, log in with JWT, and retrieve "
        "your own profile."
    ),
    version="1.0.0",
)

# CORS — open by default for easy frontend integration during development.
# Tighten ``allow_origins`` to your frontend's origin(s) in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/", tags=["Meta"])
def root():
    """Simple health/info endpoint."""
    return {"status": "ok", "docs": "/docs"}
