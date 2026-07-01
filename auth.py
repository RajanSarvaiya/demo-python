"""
auth.py
-------
JWT authentication helpers.

Provides token creation and a FastAPI dependency (`get_current_user`) that
reads a Bearer token from the `Authorization` header, validates it, and
returns the matching user.
"""

import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import crud
import models
from database import get_db

# Load variables from the local `.env` file into the environment.
load_dotenv()

# Token signing configuration. Override these via environment variables
# (e.g. a .env file) in production. NEVER ship the default secret.
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Extracts the token from an "Authorization: Bearer <token>" header and
# makes it show up as an authorize button in Swagger UI.
bearer_scheme = HTTPBearer()


def create_access_token(user_id: int) -> str:
    """Create a signed JWT whose subject is the given user id."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    FastAPI dependency: validate the Bearer token and return the user.

    Raises 401 if the token is missing, invalid, expired, or points at a
    user that no longer exists.
    """
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise invalid_credentials
    except jwt.PyJWTError:
        raise invalid_credentials

    user = crud.get_user_by_id(db, int(user_id))
    if user is None:
        raise invalid_credentials

    return user
