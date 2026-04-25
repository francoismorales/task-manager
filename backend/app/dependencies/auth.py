"""FastAPI dependencies for dependency injection.

Centralizes wiring so routers stay declarative:
- DB session
- Repository / service factories
- ``get_current_user`` to protect endpoints
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import JWTError, decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

# --- HTTP Bearer scheme (Swagger UI shows the "Authorize" button) -----------
_bearer_scheme = HTTPBearer(auto_error=False)


# --- Type aliases for cleaner router signatures -----------------------------
DbSession = Annotated[Session, Depends(get_db)]


# --- Repository / service factories ----------------------------------------
def get_user_repository(db: DbSession) -> UserRepository:
    return UserRepository(db)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repository)]


def get_auth_service(user_repo: UserRepoDep) -> AuthService:
    return AuthService(user_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


# --- Authentication ---------------------------------------------------------
def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
    user_repo: UserRepoDep,
) -> User:
    """Resolve the authenticated user from the ``Authorization: Bearer`` header.

    Raises 401 with WWW-Authenticate header per RFC 6750 if the token is
    missing, malformed, expired or references a non-existent user.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized

    try:
        payload = decode_access_token(credentials.credentials)
    except JWTError:
        raise unauthorized

    raw_sub = payload.get("sub")
    if not raw_sub:
        raise unauthorized

    try:
        user_id = int(raw_sub)
    except (TypeError, ValueError):
        raise unauthorized

    user = user_repo.get_by_id(user_id)
    if user is None:
        raise unauthorized

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]