"""Project-specific FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DbSession, UserRepoDep
from app.repositories.project_repository import ProjectRepository
from app.services.project_service import ProjectService


def get_project_repository(db: DbSession) -> ProjectRepository:
    return ProjectRepository(db)


ProjectRepoDep = Annotated[ProjectRepository, Depends(get_project_repository)]


def get_project_service(
    project_repo: ProjectRepoDep,
    user_repo: UserRepoDep,
) -> ProjectService:
    return ProjectService(project_repo, user_repo)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]