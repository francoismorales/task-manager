"""Security primitives: password hashing and JWT encode/decode.

Uses ``bcrypt`` directly (passlib is unmaintained and breaks with modern
bcrypt). Independent of FastAPI / SQLAlchemy so it can be tested in isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# Bcrypt has a hard 72-byte input limit. We truncate to keep behaviour
# predictable and avoid leaking a 500 if a user sends an unusually long
# password. 72 bytes of entropy is well above any reasonable security need.
_BCRYPT_MAX_BYTES = 72


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def _to_bcrypt_input(password: str) -> bytes:
    """Encode and truncate a password to bcrypt's accepted input size."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash for the given plain-text password."""
    hashed = bcrypt.hashpw(_to_bcrypt_input(plain_password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            _to_bcrypt_input(plain_password),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # Malformed stored hash → treat as non-match instead of erroring out.
        return False


# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT with `sub` set to the given subject (typically user id)."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT. Raises ``JWTError`` if invalid/expired."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "JWTError",
]