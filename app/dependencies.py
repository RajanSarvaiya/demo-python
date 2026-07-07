"""
dependencies.py
---------------
Reusable FastAPI dependencies.

``get_current_user`` protects endpoints by reading a Bearer token via the
``OAuth2PasswordBearer`` scheme (spec requirement), decoding it, and loading the
matching user from the database.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services import auth_service

# ``HTTPBearer`` renders a single "Value" field in Swagger's Authorize dialog:
# paste the JWT there (Swagger sends it as ``Authorization: Bearer <token>``).
bearer_scheme = HTTPBearer(description="Paste your JWT access token here.")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve the authenticated user from the Bearer token.

    Raises 401 if the token is missing, invalid, expired, or references a user
    that no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id = auth_service.decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user
