"""Smoke tests for the authentication flow.

These cover the full request → response path through the app using FastAPI's
TestClient with an in-memory SQLite database. They demonstrate that:

- The layer separation (router → service → repo) wires up correctly via DI
- Domain exceptions translate to the right HTTP status codes
- Pydantic validation runs before the route handler
"""

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str = "alice@example.com") -> str:
    """Register a user and return the JWT access token."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "full_name": "Alice Anderson",
            "password": "supersecret",
        },
    )
    assert response.status_code == 201, response.text
    token = response.json()["access_token"]
    assert token
    return token


class TestRegister:
    def test_returns_201_and_token(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "full_name": "New User",
                "password": "supersecret",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["token_type"] == "bearer"
        assert isinstance(body["access_token"], str)

    def test_duplicate_email_returns_409(self, client: TestClient):
        _register(client, "dup@example.com")
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "full_name": "Other",
                "password": "anotherpass",
            },
        )
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()

    def test_short_password_returns_422(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "x@example.com",
                "full_name": "X",
                "password": "short",
            },
        )
        assert response.status_code == 422


class TestLogin:
    def test_correct_credentials_return_token(self, client: TestClient):
        _register(client)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "supersecret"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_wrong_password_returns_401(self, client: TestClient):
        _register(client)
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "wrongpass"},
        )
        assert response.status_code == 401
        # 401 must include the WWW-Authenticate header per RFC 6750
        assert "WWW-Authenticate" in response.headers

    def test_unknown_user_returns_401(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "ghost@example.com", "password": "whatever"},
        )
        assert response.status_code == 401


class TestMe:
    def test_returns_current_user(self, client: TestClient):
        token = _register(client)
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "alice@example.com"
        assert body["full_name"] == "Alice Anderson"
        assert "id" in body
        assert "hashed_password" not in body  # never leak the hash

    def test_missing_token_returns_401(self, client: TestClient):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, client: TestClient):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.token"},
        )
        assert response.status_code == 401


class TestProjectsRequireAuth:
    def test_list_projects_without_token_returns_401(self, client: TestClient):
        response = client.get("/api/v1/projects")
        assert response.status_code == 401

    def test_list_projects_authenticated_returns_empty_list(self, client: TestClient):
        token = _register(client)
        response = client.get(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json() == []