"""
routers/users.py
----------------
User routes: ``GET /api/users/me``.
"""

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the logged-in user's profile",
)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Return the authenticated user's profile — the same data supplied at
    registration.

    Requires an ``Authorization: Bearer <token>`` header.

    Errors:
      * 401 Unauthorized - token missing, invalid, or expired
    """
    return current_user
