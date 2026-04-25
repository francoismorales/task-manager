"""Project repository: data access for Project and ProjectMember.

Encapsulates all SQLAlchemy queries so services stay storage-agnostic.
Eager-loads owner and members to avoid N+1 queries on the detail endpoint.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import ProjectRole
from app.models.project import Project, ProjectMember


class ProjectRepository:
    """Data access for the ``projects`` and ``project_members`` tables."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # --- Reads -------------------------------------------------------------
    def get_by_id(self, project_id: int) -> Project | None:
        """Fetch a project by id (no eager loading)."""
        return self._db.get(Project, project_id)

    def get_detail(self, project_id: int) -> Project | None:
        """Fetch a project with its owner and members eager-loaded.

        Used for the detail endpoint to keep response building free of
        lazy-load surprises.
        """
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
        """List projects where the user is a member (owner or otherwise).

        Ordered by most recently updated for a sensible default UX.
        """
        stmt = (
            select(Project)
            .join(ProjectMember, ProjectMember.project_id == Project.id)
            .where(ProjectMember.user_id == user_id)
            .order_by(Project.updated_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def get_member(
        self, project_id: int, user_id: int
    ) -> ProjectMember | None:
        """Return the membership record linking ``user_id`` to ``project_id``."""
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return self._db.execute(stmt).scalar_one_or_none()

    # --- Writes ------------------------------------------------------------
    def create_with_owner(
        self,
        *,
        name: str,
        description: str | None,
        deadline,  # noqa: ANN001 — date | None, kept loose to avoid imports here
        owner_id: int,
    ) -> Project:
        """Create a project and add the owner as a member with role OWNER.

        Both inserts run in the same transaction: if member creation fails,
        the project insert is rolled back.
        """
        project = Project(
            name=name,
            description=description,
            deadline=deadline,
            owner_id=owner_id,
        )
        self._db.add(project)
        self._db.flush()  # populates project.id without committing

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
        """Apply non-None fields to the project and persist."""
        for key, value in fields.items():
            if value is not None:
                setattr(project, key, value)
        self._db.commit()
        self._db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        """Delete a project. Cascades to members and tasks via FKs."""
        self._db.delete(project)
        self._db.commit()