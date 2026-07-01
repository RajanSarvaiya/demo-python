"""
models.py
---------
SQLAlchemy ORM model definitions.

Contains the `User` model which maps to the `users` table in the database.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime

from database import Base


class User(Base):
    """Represents a registered user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    # Email must be unique so the same address cannot register twice.
    email = Column(String(255), unique=True, index=True, nullable=False)
    # We never store the raw password, only a bcrypt hash.
    password_hash = Column(String(255), nullable=False)
    faculty = Column(String(255), nullable=False)
    # Skills are stored as a comma-separated string.
    skills = Column(Text, nullable=True)
    job_description = Column(Text, nullable=True)
    company = Column(String(255), nullable=True)
    experience_years = Column(Integer, nullable=True)
    portfolio_url = Column(String(512), nullable=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
