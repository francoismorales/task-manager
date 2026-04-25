"""Project repository: data access for Project and ProjectMember.

Encapsulates all SQLAlchemy queries so services stay storage-agnostic.
Eager-loads owner and members to avoid N+1 queries on the detail endpoint.
"""

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.models.enums import ProjectRole
from app.models.project import Project, ProjectMember
from app.models.task import Task


class ProjectRepository:
    """Data access for the ``projects`` and ``project_members`` tables."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- Project reads ----------------------------------------------------
    def get_by_id(self, project_id: int) -> Project | None:
        return self._db.get(Project, project_id)

    def get_detail(self, project_id: int) -> Project | None:
        """Fetch a project with its owner and members eager-loaded."""
        stmt = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.owner),
                selectinload(Project.members).selectinload(ProjectMember.user),
            )
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def list_for_user(self, user_id: int) -> list[Project]:
        stmt = (
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.updated_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    # --- Membership reads -------------------------------------------------
    def get_member(
        self, project_id: int, user_id: int
    ) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def get_member_with_user(
        self, project_id: int, user_id: int
    ) -> ProjectMember | None:
        """Same as ``get_member`` but eager-loads the user (for responses)."""
        stmt = (
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
            .options(selectinload(ProjectMember.user))
        )
        return self._db.execute(stmt).scalar_one_or_none()

    # --- Project writes ---------------------------------------------------
    def create_with_owner(
        self,
        *,
        name: str,
        description: str | None,
        deadline,  # noqa: ANN001 — date | None
        owner_id: int,
    ) -> Project:
        """Create a project and add the owner as a member with role OWNER."""
        project = Project(
            name=name,
            description=description,
            deadline=deadline,
            owner_id=owner_id,
        )
        self._db.add(project)
        self._db.flush()

        membership = ProjectMember(
            project_id=project.id,
            user_id=owner_id,
            role=ProjectRole.OWNER,
        )
        self._db.add(membership)

        self._db.commit()
        self._db.refresh(project)
        return project

    def update(self, project: Project, **fields) -> Project:
        for key, value in fields.items():
            if value is not None:
                setattr(project, key, value)
        self._db.commit()
        self._db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self._db.delete(project)
        self._db.commit()

    # --- Membership writes ------------------------------------------------
    def add_member(
        self,
        *,
        project_id: int,
        user_id: int,
        role: ProjectRole = ProjectRole.MEMBER,
    ) -> ProjectMember:
        """Insert a new membership and return it with ``user`` eager-loaded."""
        membership = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            role=role,
        )
        self._db.add(membership)
        self._db.commit()

        loaded = self.get_member_with_user(project_id, user_id)
        assert loaded is not None  # always exists immediately after commit
        return loaded

    def remove_member(self, membership: ProjectMember) -> None:
        """Remove a member and clear their task assignments in the project.

        Both operations run in the same transaction so we never end up with
        a non-member still assigned to a task. The DB-level ``ON DELETE
        SET NULL`` only fires when a user is fully deleted, not when their
        membership ends — so we do the bulk update explicitly.
        """
        project_id = membership.project_id
        user_id = membership.user_id

        # Unassign the user from all tasks in this project
        unassign_stmt = (
            update(Task)
            .where(
                Task.project_id == project_id,
                Task.assignee_id == user_id,
            )
            .values(assignee_id=None)
        )
        self._db.execute(unassign_stmt)

        # Then remove the membership
        self._db.delete(membership)
        self._db.commit()