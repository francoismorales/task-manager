"""Tasks router: nested under ``/projects/{project_id}/tasks``.

The nested URL makes the relationship explicit and lets us validate
membership once via the path. All endpoints require authentication.
"""

from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import CurrentUser, TaskServiceDep
from app.models.enums import TaskPriority, TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskDetailResponse,
    TaskUpdate,
)

router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["tasks"],
)


@router.get(
    "",
    response_model=list[TaskDetailResponse],
    summary="List tasks of a project, with optional filters",
    responses={
        403: {"description": "User is not a member of the project"},
        404: {"description": "Project not found"},
    },
)
def list_tasks(
    project_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
    status: Annotated[TaskStatus | None, Query()] = None,
    priority: Annotated[TaskPriority | None, Query()] = None,
    assignee_id: Annotated[int | None, Query()] = None,
) -> list[TaskDetailResponse]:
    tasks = task_service.list_for_project(
        project_id,
        current_user.id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
    )
    return [TaskDetailResponse.model_validate(t) for t in tasks]


@router.post(
    "",
    response_model=TaskDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task in the project",
    responses={
        400: {"description": "Assignee is not a member of the project"},
        403: {"description": "User is not a member of the project"},
        404: {"description": "Project not found"},
        422: {"description": "Validation error"},
    },
)
def create_task(
    project_id: int,
    payload: TaskCreate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskDetailResponse:
    task = task_service.create_for_project(project_id, current_user.id, payload)
    return TaskDetailResponse.model_validate(task)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get a task by id",
    responses={
        403: {"description": "User is not a member of the project"},
        404: {"description": "Task not found"},
    },
)
def get_task(
    project_id: int,
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskDetailResponse:
    task = task_service.get_for_user(project_id, task_id, current_user.id)
    return TaskDetailResponse.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Update a task (any project member)",
    responses={
        400: {"description": "Assignee is not a member of the project"},
        403: {"description": "User is not a member of the project"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error"},
    },
)
def update_task(
    project_id: int,
    task_id: int,
    payload: TaskUpdate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> TaskDetailResponse:
    task = task_service.update_for_user(
        project_id, task_id, current_user.id, payload
    )
    return TaskDetailResponse.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task (any project member)",
    responses={
        403: {"description": "User is not a member of the project"},
        404: {"description": "Task not found"},
    },
)
def delete_task(
    project_id: int,
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
) -> None:
    task_service.delete_for_user(project_id, task_id, current_user.id)