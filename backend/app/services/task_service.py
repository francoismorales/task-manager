"""Task service: business rules for task management.

Authorization rules enforced here:
- Only members of a project can list/create/update/delete its tasks.
- The assignee (if any) must be a member of the same project.
- A task cannot be moved between projects (project_id is immutable post-create).
"""

from app.core.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Use cases for task management."""

    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._tasks = task_repository
        self._projects = project_repository

    # --- Queries -----------------------------------------------------------
    def list_for_project(
        self,
        project_id: int,
        user_id: int,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> list[Task]:
        """List tasks of a project. The user must be a member."""
        self._require_member(project_id, user_id)
        return self._tasks.list_for_project(
            project_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )

    def get_for_user(self, project_id: int, task_id: int, user_id: int) -> Task:
        """Fetch a task ensuring it belongs to the project and user is a member."""
        self._require_member(project_id, user_id)
        task = self._tasks.get_by_id(task_id)
        if task is None or task.project_id != project_id:
            raise NotFoundError("Task not found")
        return task

    # --- Commands ----------------------------------------------------------
    def create_for_project(
        self,
        project_id: int,
        user_id: int,
        payload: TaskCreate,
    ) -> Task:
        """Create a task in the given project."""
        self._require_member(project_id, user_id)
        if payload.assignee_id is not None:
            self._require_assignee_is_member(project_id, payload.assignee_id)

        return self._tasks.create(
            project_id=project_id,
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            assignee_id=payload.assignee_id,
        )

    def update_for_user(
        self,
        project_id: int,
        task_id: int,
        user_id: int,
        payload: TaskUpdate,
    ) -> Task:
        """Update a task. Any project member can edit any task in the project."""
        task = self.get_for_user(project_id, task_id, user_id)

        # exclude_unset supports partial updates including explicit
        # ``assignee_id=null`` (unassign).
        updates = payload.model_dump(exclude_unset=True)

        if "assignee_id" in updates and updates["assignee_id"] is not None:
            self._require_assignee_is_member(project_id, updates["assignee_id"])

        if not updates:
            return task

        return self._tasks.update(task, **updates)

    def delete_for_user(self, project_id: int, task_id: int, user_id: int) -> None:
        """Delete a task. Any project member can delete tasks in the project."""
        task = self.get_for_user(project_id, task_id, user_id)
        self._tasks.delete(task)

    # --- Internal helpers --------------------------------------------------
    def _require_member(self, project_id: int, user_id: int) -> None:
        """Verify the project exists and the user is a member."""
        project = self._projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        if self._projects.get_member(project_id, user_id) is None:
            raise PermissionDeniedError("You are not a member of this project")

    def _require_assignee_is_member(self, project_id: int, assignee_id: int) -> None:
        """Validate that the candidate assignee is a member of the project."""
        if self._projects.get_member(project_id, assignee_id) is None:
            raise ValidationError(
                "The assignee must be a member of the project"
            )