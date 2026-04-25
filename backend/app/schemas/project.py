from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import ProjectRole
from app.schemas.user import UserResponse


class ProjectBase(BaseModel):
    """Campos comunes de un proyecto."""

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    deadline: date | None = None


class ProjectCreate(ProjectBase):
    """Payload para crear un proyecto. El owner se toma del usuario autenticado."""


class ProjectUpdate(BaseModel):
    """Todos los campos opcionales: PATCH parcial."""

    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    deadline: date | None = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(BaseModel):
    """Representación de un miembro dentro de un proyecto."""

    id: int
    user: UserResponse
    role: ProjectRole
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    """Proyecto con su lista de miembros (usado en GET /projects/{id})."""

    owner: UserResponse
    members: list[ProjectMemberResponse]


class ProjectMemberInvite(BaseModel):
    """Invitar a un miembro al proyecto por email.

    Buscar por email es más natural que pedir un user_id: el invitador
    no necesita conocer IDs internos.
    """

    email: EmailStr