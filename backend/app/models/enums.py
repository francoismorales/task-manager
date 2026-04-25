from enum import Enum


class TaskStatus(str, Enum):
    """Estados posibles de una tarea."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """Niveles de prioridad de una tarea."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ProjectRole(str, Enum):
    """Rol de un usuario dentro de un proyecto."""

    OWNER = "owner"
    MEMBER = "member"