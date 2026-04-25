"""ORM models package.

Importing the models here ensures they are registered on the SQLAlchemy
``Base.metadata`` before Alembic introspects it for autogeneration.
"""

from app.models.enums import ProjectRole, TaskPriority, TaskStatus
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.user import User

__all__ = [
    "User",
    "Project",
    "ProjectMember",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "ProjectRole",
]