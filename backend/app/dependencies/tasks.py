"""Task-specific FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DbSession
from app.dependencies.projects import ProjectRepoDep
from app.repositories.task_repository import TaskRepository
from app.services.task_service import TaskService


def get_task_repository(db: DbSession) -> TaskRepository:
    return TaskRepository(db)


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repository)]


def get_task_service(
    task_repo: TaskRepoDep,
    project_repo: ProjectRepoDep,
) -> TaskService:
    return TaskService(task_repo, project_repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]