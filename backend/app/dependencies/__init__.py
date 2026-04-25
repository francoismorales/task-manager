"""Reusable FastAPI dependencies."""

from app.dependencies.auth import (
    AuthServiceDep,
    CurrentUser,
    DbSession,
    UserRepoDep,
    get_auth_service,
    get_current_user,
    get_user_repository,
)
from app.dependencies.projects import (
    ProjectRepoDep,
    ProjectServiceDep,
    get_project_repository,
    get_project_service,
)
from app.dependencies.tasks import (
    TaskRepoDep,
    TaskServiceDep,
    get_task_repository,
    get_task_service,
)

__all__ = [
    # Auth
    "AuthServiceDep",
    "CurrentUser",
    "DbSession",
    "UserRepoDep",
    "get_auth_service",
    "get_current_user",
    "get_user_repository",
    # Projects
    "ProjectRepoDep",
    "ProjectServiceDep",
    "get_project_repository",
    "get_project_service",
    # Tasks
    "TaskRepoDep",
    "TaskServiceDep",
    "get_task_repository",
    "get_task_service",
]