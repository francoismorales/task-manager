"""Project service: business rules for projects.

Authorization rules enforced here:
- Only members of a project can read it.
- Only the owner can update or delete it.

Services raise domain exceptions; the router maps them to HTTP responses.
"""

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Use cases for project management."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._projects = project_repository

    # --- Queries -----------------------------------------------------------
    def list_for_user(self, user_id: int) -> list[Project]:
        """Return projects the user is a member of."""
        return self._projects.list_for_user(user_id)

    def get_for_user(self, project_id: int, user_id: int) -> Project:
        """Fetch a project with details, enforcing membership.

        Raises:
            NotFoundError: project does not exist.
            PermissionDeniedError: project exists but user is not a member.
        """
        project = self._projects.get_detail(project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if self._projects.get_member(project_id, user_id) is None:
            raise PermissionDeniedError("You are not a member of this project")

        return project

    # --- Commands ----------------------------------------------------------
    def create_for_user(self, payload: ProjectCreate, owner_id: int) -> Project:
        """Create a project owned by ``owner_id`` and seed the owner membership."""
        return self._projects.create_with_owner(
            name=payload.name,
            description=payload.description,
            deadline=payload.deadline,
            owner_id=owner_id,
        )

    def update_for_user(
        self,
        project_id: int,
        user_id: int,
        payload: ProjectUpdate,
    ) -> Project:
        """Update a project. Only the owner can modify it."""
        project = self._require_owner(project_id, user_id)
        return self._projects.update(
            project,
            name=payload.name,
            description=payload.description,
            deadline=payload.deadline,
        )

    def delete_for_user(self, project_id: int, user_id: int) -> None:
        """Delete a project. Only the owner can perform this action."""
        project = self._require_owner(project_id, user_id)
        self._projects.delete(project)

    # --- Internal helpers --------------------------------------------------
    def _require_owner(self, project_id: int, user_id: int) -> Project:
        """Load the project and verify the user is its owner."""
        project = self._projects.get_by_id(project_id)
        if project is None:
            raise NotFoundError("Project not found")
        if project.owner_id != user_id:
            raise PermissionDeniedError(
                "Only the project owner can perform this action"
            )
        return project