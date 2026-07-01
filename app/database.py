"""
database.py
-----------
SQLAlchemy engine, session factory, and declarative base.

Works with both SQLite (local dev) and PostgreSQL (production) depending on the
``DATABASE_URL`` setting. The ``check_same_thread`` connect arg is only applied
for SQLite, where it is required (and only valid) under FastAPI's threaded
request handling.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# ``check_same_thread=False`` is a SQLite-only requirement; passing it to any
# other driver raises an error, so apply it conditionally.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# Session factory: calling ``SessionLocal()`` produces a new Session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base that all ORM models inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency yielding a database session and guaranteeing it is
    closed after the request completes, even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
