"""User repository: only this layer talks to the SQLAlchemy session for User.

Keeping persistence isolated lets us swap the storage layer without touching
services, and makes services testable with a fake repository.
"""

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Data access for the ``users`` table."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- Reads -------------------------------------------------------------
    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._db.query(User).filter(User.email == email).one_or_none()

    def list_all(self) -> list[User]:
        return self._db.query(User).order_by(User.full_name).all()

    # --- Writes ------------------------------------------------------------
    def create(self, *, email: str, full_name: str, hashed_password: str) -> User:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
        )
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user