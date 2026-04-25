"""Authentication service: business logic for register/login.

Uses domain exceptions; HTTP concerns live in the router layer.
"""

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    """Coordinates password hashing, token issuance and user persistence."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._users = user_repository

    def register(self, payload: UserCreate) -> User:
        """Create a new user. Raises ``ConflictError`` if email is taken."""
        if self._users.get_by_email(payload.email) is not None:
            raise ConflictError("Email already registered")

        return self._users.create(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )

    def authenticate(self, email: str, password: str) -> User:
        """Validate credentials. Raises ``AuthenticationError`` on failure.

        We deliberately use a single error message regardless of whether the
        user exists, to avoid email enumeration.
        """
        user = self._users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        return user

    def issue_token_for(self, user: User) -> str:
        """Create a signed JWT for the given user."""
        return create_access_token(subject=user.id)

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch a user or raise ``NotFoundError``."""
        user = self._users.get_by_id(user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user