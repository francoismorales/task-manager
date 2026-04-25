"""Seed script: populates the database with sample data for local development.

Usage (from /backend with venv active):
    python -m app.seed

Idempotent: skips creation if a user with the same email already exists.
All seeded users share the same password 'password123' for convenience.
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import (
    Project,
    ProjectMember,
    ProjectRole,
    Task,
    TaskPriority,
    TaskStatus,
    User,
)

SEED_PASSWORD = "password123"  # noqa: S105 — local dev only


def _get_or_create_user(
    db: Session, email: str, full_name: str, password_hash: str
) -> User:
    user = db.query(User).filter(User.email == email).one_or_none()
    if user is None:
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=password_hash,
        )
        db.add(user)
        db.flush()
    return user


def seed(db: Session) -> None:
    # Hash the password once and reuse — bcrypt is intentionally slow.
    pwd = hash_password(SEED_PASSWORD)

    alice = _get_or_create_user(db, "alice@example.com", "Alice Anderson", pwd)
    bob = _get_or_create_user(db, "bob@example.com", "Bob Brown", pwd)
    carol = _get_or_create_user(db, "carol@example.com", "Carol Castro", pwd)

    # Skip if there's already a project — keeps the script idempotent.
    if db.query(Project).count() > 0:
        db.commit()
        print(f"Seed skipped: projects already exist. Login with any of "
              f"alice@example.com / bob@example.com / carol@example.com "
              f"(password: {SEED_PASSWORD}).")
        return

    today = date.today()

    project = Project(
        name="Lanzamiento Q2",
        description="Preparación del lanzamiento del producto en el segundo trimestre.",
        deadline=today + timedelta(days=45),
        owner_id=alice.id,
    )
    db.add(project)
    db.flush()

    db.add_all([
        ProjectMember(project_id=project.id, user_id=alice.id, role=ProjectRole.OWNER),
        ProjectMember(project_id=project.id, user_id=bob.id, role=ProjectRole.MEMBER),
        ProjectMember(project_id=project.id, user_id=carol.id, role=ProjectRole.MEMBER),
    ])

    db.add_all([
        Task(
            title="Definir alcance del MVP",
            description="Documentar features mínimos para el lanzamiento.",
            status=TaskStatus.COMPLETED,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=alice.id,
        ),
        Task(
            title="Diseño de la landing page",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            assignee_id=carol.id,
        ),
        Task(
            title="Configurar pipeline CI/CD",
            status=TaskStatus.PENDING,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            assignee_id=bob.id,
        ),
        Task(
            title="Plan de comunicación",
            status=TaskStatus.PENDING,
            priority=TaskPriority.LOW,
            project_id=project.id,
            assignee_id=None,
        ),
    ])

    db.commit()
    print(
        f"Seed OK: created project '{project.name}' with 4 tasks and 3 members. "
        f"Login with alice@example.com / {SEED_PASSWORD}."
    )


def main() -> None:
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()