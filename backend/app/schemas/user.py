from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Campos compartidos por entrada/salida."""

    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)


class UserCreate(UserBase):
    """Payload para registrar un usuario nuevo."""

    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Permite editar el nombre. Email/password se manejan aparte."""

    full_name: str | None = Field(default=None, min_length=1, max_length=120)


class UserResponse(UserBase):
    """Representación pública de un usuario (sin password hash)."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)