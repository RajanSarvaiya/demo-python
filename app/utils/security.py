"""
utils/security.py
-----------------
Low-level password hashing helpers built on bcrypt.

Kept separate from JWT logic so it can be reused and unit-tested in isolation.
"""

import bcrypt

# bcrypt only considers the first 72 bytes of the input password.
_BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash (with a fresh salt) for the given password."""
    pw_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a plain-text password against a stored bcrypt hash."""
    pw_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(pw_bytes, password_hash.encode("utf-8"))
