"""Project service: business rules for projects and team membership.

Authorization rules enforced here:
- Only members of a project can read it.
- Only the owner can update or delete the project.
- Only the owner can add or remove members.
- The owner cannot be removed as a member (would leave the project headless).
- Removing a member also clears their assignments on the project's tasks
  (handled atomically in ProjectRepository.remove_member).

Services raise domain exceptions; the router maps them to HTTP responses.
"""

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.models.enums import ProjectRole
from app.models.project import Project, ProjectMember
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    """Use cases for project management."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
    ) -> None:
        self._projects = project_repository
        self._users = user_repository

    # --- Project queries --------------------------------------------------
    def list_for_user(self, user_id: int) -> list[Project]:
        return self._projects.list_for_user(user_id)

    def get_for_user(self, project_id: int, user_id: int) -> Project:
        """Fetch a project with details. The user must be a member."""
        project = self._projects.get_detail(project_id)
        if project is None:
            raise NotFoundError("Project not found")

        if self._projects.get_member(project_id, user_id) is None:
            raise PermissionDeniedError("You are not a member of this project")

        return project

    # --- Project commands -------------------------------------------------
    def create_for_user(self, payload: ProjectCreate, owner_id: int) -> Project:
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
        project = self._require_owner(project_id, user_id)
        return self._projects.update(
            project,
            name=payload.name,
            description=payload.description,
            deadline=payload.deadline,
        )

    def delete_for_user(self, project_id: int, user_id: int) -> None:
        project = self._require_owner(project_id, user_id)
        self._projects.delete(project)

    # --- Membership commands ---------------------------------------------
    def invite_member_by_email(
        self,
        project_id: int,
        caller_id: int,
        email: str,
    ) -> ProjectMember:
        """Add a user to the project by their email address. Owner only.

        Raises:
            NotFoundError: project or user with that email does not exist.
            PermissionDeniedError: caller is not the owner.
            ConflictError: user is already a member.
        """
        self._require_owner(project_id, caller_id)

        user = self._users.get_by_email(email)
        if user is None:
            raise NotFoundError("No user found with that email")

        if self._projects.get_member(project_id, user.id) is not None:
            raise ConflictError("User is already a member of this project")

        return self._projects.add_member(
            project_id=project_id,
            user_id=user.id,
            role=ProjectRole.MEMBER,
        )

    def remove_member(
        self,
        project_id: int,
        caller_id: int,
        target_user_id: int,
    ) -> None:
        """Remove a member from the project. Owner only.

        Raises:
            NotFoundError: project does not exist or target is not a member.
            PermissionDeniedError: caller is not the owner.
            ValidationError: attempting to remove the owner.
        """
        project = self._require_owner(project_id, caller_id)

        if target_user_id == project.owner_id:
            # Self-protection: removing the owner would orphan the project.
            # Owner deletion happens via DELETE /projects/{id}.
            raise ValidationError("The project owner cannot be removed")

        membership = self._projects.get_member(project_id, target_user_id)
        if membership is None:
            raise NotFoundError("User is not a member of this project")

        self._projects.remove_member(membership)

    # --- Internal helpers -------------------------------------------------
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