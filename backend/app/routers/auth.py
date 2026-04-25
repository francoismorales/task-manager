"""Auth router: registration, login and current user retrieval.

Thin HTTP boundary: parses input, calls the service, returns a response.
Domain exceptions raised by the service are translated to HTTP responses by
the global handlers registered in ``app.core.error_handlers``.
"""

from fastapi import APIRouter, status

from app.dependencies import AuthServiceDep, CurrentUser
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and return an access token",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
def register(payload: UserCreate, auth_service: AuthServiceDep) -> TokenResponse:
    user = auth_service.register(payload)
    token = auth_service.issue_token_for(user)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email + password and return a JWT",
    responses={
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"},
    },
)
def login(payload: LoginRequest, auth_service: AuthServiceDep) -> TokenResponse:
    user = auth_service.authenticate(payload.email, payload.password)
    token = auth_service.issue_token_for(user)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the currently authenticated user",
    responses={401: {"description": "Missing or invalid token"}},
)
def read_current_user(current_user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(current_user)