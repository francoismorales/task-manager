"""Task repository: data access for the ``tasks`` table.

Read methods support optional filters (status, priority, assignee) applied
at the SQL level, not in Python, to keep things efficient at scale.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import TaskPriority, TaskStatus
from app.models.task import Task


class TaskRepository:
    """Data access for the ``tasks`` table."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- Reads -------------------------------------------------------------
    def get_by_id(self, task_id: int) -> Task | None:
        """Fetch a task by id with assignee eager-loaded."""
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.assignee))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def list_for_project(
        self,
        project_id: int,
        *,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        assignee_id: int | None = None,
    ) -> list[Task]:
        """List tasks belonging to a project with optional filters.

        Ordered by recency. Eager-loads assignee to avoid N+1 in the response.
        """
        stmt = (
            select(Task)
            .where(Task.project_id == project_id)
            .options(selectinload(Task.assignee))
        )

        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if assignee_id is not None:
            stmt = stmt.where(Task.assignee_id == assignee_id)

        stmt = stmt.order_by(Task.created_at.desc())

        return list(self._db.execute(stmt).scalars().all())

    # --- Writes ------------------------------------------------------------
    def create(
        self,
        *,
        project_id: int,
        title: str,
        description: str | None,
        status: TaskStatus,
        priority: TaskPriority,
        assignee_id: int | None,
    ) -> Task:
        task = Task(
            project_id=project_id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
        )
        self._db.add(task)
        self._db.commit()
        self._db.refresh(task)
        return task

    def update(self, task: Task, **fields) -> Task:
        """Apply only the provided fields. ``assignee_id`` can be set to
        None explicitly to unassign — pass ``assignee_id=None`` in kwargs.
        """
        for key, value in fields.items():
            setattr(task, key, value)
        self._db.commit()
        self._db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self._db.delete(task)
        self._db.commit()