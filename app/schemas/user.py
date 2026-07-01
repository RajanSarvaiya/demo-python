"""
schemas/user.py
---------------
Pydantic v2 request/response models.

* ``UserCreate``   - validates the ``POST /api/register`` body.
* ``UserResponse`` - shapes the user JSON returned by register / users/me.
                     Deliberately omits ``password_hash``.
* ``Token``        - the login access-token payload.
"""

import re
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# Loose E.164-style phone check: optional leading '+', then 7-15 digits.
_PHONE_RE = re.compile(r"^\+?\d{7,15}$")


class UserCreate(BaseModel):
    """Registration input. All job fields required except ``job_description``."""

    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Valid, unique email address")
    phone_number: str = Field(
        ..., min_length=7, max_length=20, description="Unique phone number"
    )
    password: str = Field(
        ..., min_length=8, description="At least 8 characters"
    )
    job_title: str = Field(..., min_length=1, max_length=150)
    skills: List[str] = Field(
        ..., min_length=1, description="Non-empty list of skills"
    )
    job_description: Optional[str] = Field(None, description="Optional summary")

    @field_validator("name", "job_title")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Reject whitespace-only required strings and trim surrounding space."""
        if not value or not value.strip():
            raise ValueError("This field cannot be empty.")
        return value.strip()

    @field_validator("phone_number")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        """Normalise and validate the phone number format."""
        cleaned = value.strip()
        if not _PHONE_RE.match(cleaned):
            raise ValueError(
                "Phone number must be 7-15 digits, optionally prefixed with '+'."
            )
        return cleaned

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, value: List[str]) -> List[str]:
        """Trim each skill and drop blanks; require at least one real skill."""
        cleaned = [s.strip() for s in value if s and s.strip()]
        if not cleaned:
            raise ValueError("At least one non-empty skill is required.")
        return cleaned

    @field_validator("job_description", mode="before")
    @classmethod
    def empty_to_none(cls, value):
        """Convert an empty/whitespace description to None."""
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip() if isinstance(value, str) else value


class UserResponse(BaseModel):
    """User JSON returned to clients. Never includes the password hash."""

    id: UUID
    name: str
    email: EmailStr
    phone_number: str
    job_title: str
    skills: List[str]
    job_description: Optional[str] = None
    created_at: datetime

    # Build directly from a SQLAlchemy ``User`` instance.
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT access token returned by ``POST /api/login``."""

    access_token: str = Field(..., description="Signed JWT bearer token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token lifetime in seconds")
