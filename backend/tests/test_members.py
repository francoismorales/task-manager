"""Tests for project membership management (Phase 6)."""

from fastapi.testclient import TestClient


def _register(client: TestClient, email: str, full_name: str = "User") -> str:
    """Register a user and return their JWT token."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": full_name, "password": "supersecret"},
    )
    assert response.status_code == 201, response.text
    return response.json()["access_token"]


def _create_project(client: TestClient, token: str, name: str = "P1") -> dict:
    response = client.post(
        "/api/v1/projects",
        json={"name": name},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


class TestInviteMember:
    def test_owner_can_invite_existing_user_by_email(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)

        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        assert response.status_code == 201
        body = response.json()
        assert body["user"]["email"] == "guest@x.com"
        assert body["role"] == "member"

    def test_inviting_unknown_email_returns_404(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        project = _create_project(client, owner_token)

        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "ghost@nowhere.com"},
            headers=_auth(owner_token),
        )
        assert response.status_code == 404

    def test_inviting_existing_member_returns_409(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)

        client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        assert response.status_code == 409

    def test_non_owner_cannot_invite(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        member_token = _register(client, "member@x.com", "Member")
        _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)

        client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "member@x.com"},
            headers=_auth(owner_token),
        )

        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(member_token),
        )
        assert response.status_code == 403

    def test_invalid_email_returns_422(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        project = _create_project(client, owner_token)

        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "not-an-email"},
            headers=_auth(owner_token),
        )
        assert response.status_code == 422

    def test_unauthenticated_returns_401(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        project = _create_project(client, owner_token)

        response = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "x@x.com"},
        )
        assert response.status_code == 401


class TestRemoveMember:
    def test_owner_can_remove_member(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)
        invite_resp = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        guest_user_id = invite_resp.json()["user"]["id"]

        response = client.delete(
            f"/api/v1/projects/{project['id']}/members/{guest_user_id}",
            headers=_auth(owner_token),
        )
        assert response.status_code == 204

        detail = client.get(
            f"/api/v1/projects/{project['id']}",
            headers=_auth(owner_token),
        ).json()
        emails = [m["user"]["email"] for m in detail["members"]]
        assert "guest@x.com" not in emails

    def test_owner_cannot_be_removed(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        project = _create_project(client, owner_token)
        owner_user_id = project["owner_id"]

        response = client.delete(
            f"/api/v1/projects/{project['id']}/members/{owner_user_id}",
            headers=_auth(owner_token),
        )
        assert response.status_code == 400
        assert "owner" in response.json()["detail"].lower()

    def test_non_owner_cannot_remove(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        member_token = _register(client, "member@x.com", "Member")
        guest_token = _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)

        client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "member@x.com"},
            headers=_auth(owner_token),
        )
        invite_guest = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        guest_id = invite_guest.json()["user"]["id"]

        response = client.delete(
            f"/api/v1/projects/{project['id']}/members/{guest_id}",
            headers=_auth(member_token),
        )
        assert response.status_code == 403

        assert guest_token  # silence unused warning

    def test_removing_non_member_returns_404(self, client: TestClient):
        owner_token = _register(client, "owner@x.com", "Owner")
        project = _create_project(client, owner_token)

        response = client.delete(
            f"/api/v1/projects/{project['id']}/members/9999",
            headers=_auth(owner_token),
        )
        assert response.status_code == 404


class TestCascadeOnRemove:
    def test_removing_member_unassigns_their_tasks(self, client: TestClient):
        """When a user is removed, their existing task assignments must be
        cleared."""
        owner_token = _register(client, "owner@x.com", "Owner")
        _register(client, "guest@x.com", "Guest")
        project = _create_project(client, owner_token)
        invite = client.post(
            f"/api/v1/projects/{project['id']}/members",
            json={"email": "guest@x.com"},
            headers=_auth(owner_token),
        )
        guest_id = invite.json()["user"]["id"]

        task_resp = client.post(
            f"/api/v1/projects/{project['id']}/tasks",
            json={"title": "Assigned to guest", "assignee_id": guest_id},
            headers=_auth(owner_token),
        )
        assert task_resp.status_code == 201
        task_id = task_resp.json()["id"]

        remove_resp = client.delete(
            f"/api/v1/projects/{project['id']}/members/{guest_id}",
            headers=_auth(owner_token),
        )
        assert remove_resp.status_code == 204

        task_after = client.get(
            f"/api/v1/projects/{project['id']}/tasks/{task_id}",
            headers=_auth(owner_token),
        ).json()
        assert task_after["assignee"] is None
        assert task_after["assignee_id"] is None