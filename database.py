"""
database.py
-----------
Sets up the SQLAlchemy engine, session factory, and declarative base.

We use a local SQLite database file (`app.db`) so that registered users
persist between requests and server restarts.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load variables from the local `.env` file into the environment.
load_dotenv()

# Database connection URL, read from the environment. Falls back to a local
# SQLite file (`app.db`) if DATABASE_URL is not set.
# Examples:
#   sqlite:///./app.db
#   postgresql+psycopg2://user:password@localhost:5432/mydb
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# `check_same_thread=False` is only needed (and only valid) for SQLite, where
# the same connection may be accessed across different threads under FastAPI.
# Other databases (PostgreSQL, MySQL) must not receive this argument.
connect_args = (
    {"check_same_thread": False}
    if SQLALCHEMY_DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=connect_args,
)

# SessionLocal is a factory that produces new Session objects when called.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all ORM models inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees it
    is closed after the request finishes (even if an exception occurs).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
