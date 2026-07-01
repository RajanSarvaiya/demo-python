"""
crud.py
-------
Database access layer.

All functions that read from or write to the database live here so the
route handlers in `main.py` stay focused on HTTP concerns.
"""

import bcrypt
from sqlalchemy.orm import Session

import models
import schemas

# bcrypt has a hard 72-byte limit on the input password.
_BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """
    Return a bcrypt hash of the given plain-text password.

    The password is encoded to UTF-8 and truncated to bcrypt's 72-byte
    limit, then hashed with a freshly generated salt. The resulting hash
    is decoded to a str for storage in the database.
    """
    pw_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    pw_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))


def get_user_by_email(db: Session, email: str) -> models.User | None:
    """Fetch a single user by email, or None if not found."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> models.User | None:
    """Fetch a single user by primary key id, or None if not found."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Create and persist a new User from validated registration data.

    The password is hashed before storage. Raises any underlying
    SQLAlchemy exception to the caller so it can be handled there.
    """
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        faculty=user.faculty,
        skills=user.skills,
        job_description=user.job_description,
        company=user.company,
        experience_years=user.experience_years,
        # HttpUrl is converted to a plain string for storage.
        portfolio_url=str(user.portfolio_url) if user.portfolio_url else None,
    )

    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        # Roll back so the session stays usable after a failed write.
        db.rollback()
        raise
