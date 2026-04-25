"""Pytest configuration and shared fixtures.

We use an in-memory SQLite DB per test session to keep tests fast and
isolated from any local development database. The whole schema is created
from SQLAlchemy metadata (no Alembic in tests) — Alembic is verified
separately by being run in CI / deploy.
"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import create_app

# In-memory SQLite shared across the connection pool (StaticPool) so the
# schema persists between calls within a test.
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def engine():
    eng = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture
def db_session(engine) -> Generator:
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(engine) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the DB dependency overridden to use SQLite."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()