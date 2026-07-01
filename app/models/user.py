"""
models/user.py
--------------
SQLAlchemy ORM model for the ``users`` table.

Design notes for database portability (spec targets PostgreSQL, dev uses SQLite):

* ``id`` uses SQLAlchemy's cross-dialect :class:`~sqlalchemy.Uuid` type. On
  PostgreSQL this maps to the native ``UUID`` column; on SQLite it is stored as
  a 32-char hex string. Either way the Python value is a :class:`uuid.UUID`.
* ``skills`` uses PostgreSQL's native ``ARRAY(Text)`` when available and falls
  back to a JSON column on other backends (e.g. SQLite). Both round-trip a
  Python ``list[str]``, matching the spec's "store as ... JSON array" note.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text, Uuid
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.types import JSON

from app.database import Base

# Use a native PostgreSQL text array where supported, otherwise a JSON column.
# ``with_variant`` keeps a single model definition working across both backends.
SkillsType = JSON().with_variant(ARRAY(Text()), "postgresql")


def _utcnow() -> datetime:
    """Timezone-aware current UTC time (used for created_at / updated_at)."""
    return datetime.now(timezone.utc)


class User(Base):
    """A registered user together with their job profile."""

    __tablename__ = "users"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name = Column(String(100), nullable=False)
    # Email and phone are unique so the same identity cannot register twice.
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    # Only the bcrypt hash is ever stored, never the raw password.
    password_hash = Column(String(255), nullable=False)
    job_title = Column(String(150), nullable=False)
    # A list of skill strings; required (non-empty) at the schema layer.
    skills = Column(SkillsType, nullable=False)
    job_description = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
