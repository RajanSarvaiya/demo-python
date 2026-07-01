"""
schemas.py
----------
Pydantic schemas used for validating and shaping data.

`UserCreate` validates the JSON registration body, `LoginRequest` validates
login input, and `UserOut` shapes the JSON returned to clients.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator


class UserCreate(BaseModel):
    """Schema for validating registration form submissions."""

    name: str = Field(..., min_length=1, description="Full name, required")
    email: EmailStr = Field(..., description="Valid, unique email address")
    password: str = Field(..., min_length=6, description="At least 6 characters")
    faculty: str = Field(..., min_length=1, description="Faculty / Department")
    skills: Optional[str] = Field(None, description="Comma-separated skills")
    job_description: Optional[str] = Field(None, description="Current role")
    company: Optional[str] = Field(None, description="Company name")
    experience_years: Optional[int] = Field(
        None, ge=0, le=80, description="Years of experience (optional)"
    )
    portfolio_url: Optional[HttpUrl] = Field(
        None, description="LinkedIn / Portfolio URL (optional)"
    )

    @field_validator("name", "faculty")
    @classmethod
    def not_blank(cls, value: str) -> str:
        """Reject values that are only whitespace."""
        if value is None or not value.strip():
            raise ValueError("This field cannot be empty.")
        return value.strip()

    @field_validator(
        "skills", "job_description", "company", mode="before"
    )
    @classmethod
    def empty_string_to_none(cls, value):
        """Convert empty/whitespace optional strings to None."""
        if value is None:
            return None
        if isinstance(value, str) and not value.strip():
            return None
        return value.strip() if isinstance(value, str) else value


class LoginRequest(BaseModel):
    """Schema for validating login requests."""

    email: EmailStr = Field(..., description="Registered email address")
    password: str = Field(..., min_length=1, description="Account password")


class UserOut(BaseModel):
    """
    Schema for returning a user as JSON. Deliberately excludes the
    password hash.
    """

    id: int
    name: str
    email: EmailStr
    faculty: str
    skills: Optional[str] = None
    job_description: Optional[str] = None
    company: Optional[str] = None
    experience_years: Optional[int] = None
    portfolio_url: Optional[str] = None
    created_at: datetime

    # Allow building this schema directly from a SQLAlchemy model instance.
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT access token returned by register and login, with the user."""

    access_token: str = Field(..., description="JWT bearer token")
    token_type: str = Field("bearer", description="Token type")
    user: UserOut
