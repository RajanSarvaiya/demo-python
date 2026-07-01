"""
services/auth_service.py
------------------------
Business logic for authentication: user creation, credential verification,
JWT creation and decoding.

Route handlers stay thin by delegating all of this here. Password hashing is
delegated further down to :mod:`app.utils.security`.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password


# --------------------------------------------------------------------------- #
# Data access
# --------------------------------------------------------------------------- #
def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return the user with the given email, or None."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    """Return the user with the given phone number, or None."""
    return db.query(User).filter(User.phone_number == phone_number).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
    """Return the user with the given id, or None."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    """
    Persist a new user, hashing the password first.

    Rolls back and re-raises on any database error so the session stays usable.
    """
    db_user = User(
        name=user_in.name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        password_hash=hash_password(user_in.password),
        job_title=user_in.job_title,
        skills=user_in.skills,
        job_description=user_in.job_description,
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception:
        db.rollback()
        raise


def authenticate_user(
    db: Session, email: str, password: str
) -> Optional[User]:
    """Return the user if email+password are valid, else None."""
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


# --------------------------------------------------------------------------- #
# JWT helpers
# --------------------------------------------------------------------------- #
def create_access_token(user_id: uuid.UUID) -> str:
    """Create a signed JWT whose subject (``sub``) is the user id."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> Optional[uuid.UUID]:
    """
    Validate a JWT and return the user id from its ``sub`` claim.

    Returns None if the token is invalid, expired, or malformed.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject = payload.get("sub")
        if subject is None:
            return None
        return uuid.UUID(str(subject))
    except (jwt.PyJWTError, ValueError):
        return None
