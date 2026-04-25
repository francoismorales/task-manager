"""Projects router: CRUD endpoints, all behind authentication.

Authorization is enforced inside the service: members can read, only owners
can update or delete. Domain exceptions are mapped to HTTP responses by the
global handlers, keeping this layer declarative.
"""

from fastapi import APIRouter, status

from app.dependencies import CurrentUser, ProjectServiceDep
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List projects the current user is a member of",
)
def list_projects(
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
) -> list[ProjectResponse]:
    projects = project_service.list_for_user(current_user.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project owned by the current user",
    responses={401: {"description": "Missing or invalid token"}},
)
def create_project(
    payload: ProjectCreate,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
) -> ProjectResponse:
    project = project_service.create_for_user(payload, owner_id=current_user.id)
    return ProjectResponse.model_validate(project)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get a project by id, including owner and members",
    responses={
        403: {"description": "User is not a member of the project"},
        404: {"description": "Project not found"},
    },
)
def get_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
) -> ProjectDetailResponse:
    project = project_service.get_for_user(project_id, current_user.id)
    return ProjectDetailResponse.model_validate(project)


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update a project (owner only)",
    responses={
        403: {"description": "Only the owner can update the project"},
        404: {"description": "Project not found"},
    },
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
) -> ProjectResponse:
    project = project_service.update_for_user(project_id, current_user.id, payload)
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project (owner only)",
    responses={
        403: {"description": "Only the owner can delete the project"},
        404: {"description": "Project not found"},
    },
)
def delete_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
) -> None:
    project_service.delete_for_user(project_id, current_user.id)