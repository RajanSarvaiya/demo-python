"""
main.py
-------
FastAPI application entry point.

A pure JSON REST API for user registration and lookup. There is no HTML
frontend: every endpoint accepts and returns JSON.

Run with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

import auth
import crud
import models
import schemas
from database import Base, engine, get_db

# Create the database tables on startup if they do not already exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI User App",
    description="JSON REST API for user registration and lookup.",
    version="1.0.0",
)


@app.get("/", tags=["Meta"])
def root():
    """Simple health/info endpoint."""
    return {"status": "ok", "docs": "/docs"}


@app.post(
    "/api/register",
    response_model=schemas.Token,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"],
)
def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user and return a JWT access token.

    Accepts a JSON body validated by `UserCreate`, hashes the password,
    persists the user, and returns an access token plus the created user.

    Errors:
      * 409 Conflict            - email already registered
      * 422 Unprocessable Entity - body fails validation (handled by FastAPI)
      * 500                     - database write failure
    """
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    try:
        new_user = crud.create_user(db, user_in)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save user. Please try again.",
        )

    token = auth.create_access_token(new_user.id)
    return {"access_token": token, "token_type": "bearer", "user": new_user}


@app.post(
    "/api/login",
    response_model=schemas.Token,
    tags=["Users"],
)
def login(
    credentials: schemas.LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Verify a user's email and password and return a JWT access token.

    Errors:
      * 401 Unauthorized - invalid email or password
    """
    user = crud.get_user_by_email(db, credentials.email)
    if user is None or not crud.verify_password(
        credentials.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    token = auth.create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


@app.get(
    "/api/users/me",
    response_model=schemas.UserOut,
    tags=["Users"],
)
def get_current_user(current_user: models.User = Depends(auth.get_current_user)):
    """
    Return the currently authenticated user's details.

    Requires an `Authorization: Bearer <token>` header. The user is
    identified from the token, not from the URL.

    Errors:
      * 401 Unauthorized - token missing, invalid, or expired
    """
    return current_user
