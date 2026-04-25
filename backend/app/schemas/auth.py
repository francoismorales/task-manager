from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Credenciales para autenticación."""

    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """JWT que se devuelve al hacer login o registro."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Contenido decodificado del JWT."""

    sub: str  # user id como string
    exp: int