"""Map domain exceptions to HTTP responses.

Routers stay thin: they just call services. Domain exceptions raised by
services bubble up to handlers registered here, which translate them to
the right HTTP status code and a consistent JSON body.

This is the single place where domain → HTTP mapping lives.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


def _json(detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"detail": detail})


def register_exception_handlers(app: FastAPI) -> None:
    """Wire domain exceptions to HTTP responses on the given app."""

    @app.exception_handler(NotFoundError)
    async def _not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return _json(str(exc) or "Resource not found", 404)

    @app.exception_handler(ConflictError)
    async def _conflict(_: Request, exc: ConflictError) -> JSONResponse:
        return _json(str(exc) or "Conflict", 409)

    @app.exception_handler(PermissionDeniedError)
    async def _forbidden(_: Request, exc: PermissionDeniedError) -> JSONResponse:
        return _json(str(exc) or "Forbidden", 403)

    @app.exception_handler(AuthenticationError)
    async def _unauthorized(_: Request, exc: AuthenticationError) -> JSONResponse:
        # 401 with WWW-Authenticate per RFC 6750
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc) or "Authentication required"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ValidationError)
    async def _validation(_: Request, exc: ValidationError) -> JSONResponse:
        return _json(str(exc) or "Validation error", 400)