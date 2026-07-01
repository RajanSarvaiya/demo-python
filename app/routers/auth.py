"""
routers/auth.py
---------------
Authentication routes: ``POST /api/register`` and ``POST /api/login``.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.user import Token, UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/api", tags=["Auth"])

# Documents the JSON request body in Swagger even though the handler reads the
# request manually (so it can also accept the OAuth2 form that Swagger's
# Authorize button sends). See ``login`` below.
_LOGIN_OPENAPI_EXTRA = {
    "requestBody": {
        "required": True,
        "content": {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["email", "password"],
                    "properties": {
                        "email": {"type": "string", "format": "email"},
                        "password": {"type": "string"},
                    },
                },
                "example": {
                    "email": "rahul@example.com",
                    "password": "SecurePass123",
                },
            }
        },
    }
}


async def _extract_credentials(request: Request) -> tuple[str, str]:
    """
    Pull email + password from the request.

    Supports two content types so a single ``/api/login`` endpoint serves both:
      * ``application/json``  - the documented API contract ({email, password}).
      * form-urlencoded       - the OAuth2 password flow that Swagger's
                                Authorize button submits (email in ``username``).
    """
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        try:
            data = await request.json()
        except Exception:
            data = {}
        return (data or {}).get("email", ""), (data or {}).get("password", "")

    form = await request.form()
    # OAuth2PasswordRequestForm uses ``username``; accept ``email`` too.
    email = form.get("username") or form.get("email") or ""
    return str(email), str(form.get("password") or "")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user with job profile data",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """
    Create a new user.

    Errors:
      * 409 Conflict - email or phone number already registered
      * 422          - request body fails validation (handled by FastAPI)
    """
    if auth_service.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )
    if auth_service.get_user_by_phone(db, user_in.phone_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered.",
        )

    try:
        user = auth_service.create_user(db, user_in)
    except Exception:
        # A race could still trip the unique constraint between the checks
        # above and the insert; surface it as a conflict rather than a 500.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or phone number already registered.",
        )

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and receive a JWT access token",
    openapi_extra=_LOGIN_OPENAPI_EXTRA,
)
async def login(request: Request, db: Session = Depends(get_db)) -> Token:
    """
    Verify credentials and return a JWT access token.

    Accepts the documented JSON body ``{"email": ..., "password": ...}`` and
    also the OAuth2 form used by Swagger's Authorize button.

    Errors:
      * 401 Unauthorized - invalid email or password
    """
    email, password = await _extract_credentials(request)
    user = auth_service.authenticate_user(db, email, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_service.create_access_token(user.id)
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_seconds,
    )
