"""Domain-level exceptions.

Services raise these to remain framework-agnostic. The router layer (or a
global exception handler) translates them to HTTP responses with the correct
status code and message, keeping HTTP concerns out of the business logic.
"""


class DomainError(Exception):
    """Base class for all domain errors."""


class NotFoundError(DomainError):
    """Resource does not exist."""


class ConflictError(DomainError):
    """Resource state conflicts with the request (e.g. unique key clash)."""


class AuthenticationError(DomainError):
    """Credentials are missing or invalid."""


class PermissionDeniedError(DomainError):
    """User is authenticated but not allowed to perform the action."""


class ValidationError(DomainError):
    """Business-rule validation failure (separate from Pydantic validation)."""