"""
config.py
---------
Application settings loaded from environment variables (via a local ``.env``
file when present).

The spec targets PostgreSQL, but the code is deliberately database-agnostic:
``DATABASE_URL`` defaults to a local SQLite file so the app runs out of the box,
and pointing it at ``postgresql+psycopg2://...`` switches to PostgreSQL with no
code changes.
"""

import os

from dotenv import load_dotenv

# Load variables from a local ``.env`` file into the process environment.
load_dotenv()


class Settings:
    """Typed accessors for the environment configuration."""

    # Database connection URL.
    #   sqlite:///./app.db                                    (local dev default)
    #   postgresql+psycopg2://user:password@localhost:5432/jobdb  (spec target)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # JWT signing configuration. The secret MUST be overridden in production.
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY", "change-this-to-a-long-random-secret-in-production"
    )
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )

    @property
    def access_token_expire_seconds(self) -> int:
        """Token lifetime in seconds, used for the login ``expires_in`` field."""
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60


settings = Settings()
