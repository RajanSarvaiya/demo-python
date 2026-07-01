"""
dependencies.py
---------------
Reusable FastAPI dependencies.

``get_current_user`` protects endpoints by reading a Bearer token via the
``OAuth2PasswordBearer`` scheme (spec requirement), decoding it, and loading the
matching user from the database.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services import auth_service

# ``tokenUrl`` points Swagger at the login endpoint and adds the Authorize
# button. The token is read from the ``Authorization: Bearer <token>`` header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
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

    user_id = auth_service.decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = auth_service.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user
