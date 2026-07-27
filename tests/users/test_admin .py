"""Tests for the administrative user routes (/admin/users).

All these routes require an authenticated ADMIN user. The `admin_headers`
fixture (defined in conftest.py) provides the necessary Authorization header.
"""

from tests.conftest import API_PREFIX


# ---------------------------------------------------------------------------
# Authorization
# ---------------------------------------------------------------------------
def test_admin_route_forbidden_for_member(client, auth_headers):
    """A regular MEMBER cannot access admin routes (403)."""
    response = client.get(
        f"{API_PREFIX}/admin/users/",
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_admin_route_requires_auth(client):
    """Accessing an admin route with no token returns 401."""
    response = client.get(f"{API_PREFIX}/admin/users/")

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def test_admin_create_user(client, admin_headers):
    """An admin can create a new user with a chosen role."""
    response = client.post(
        f"{API_PREFIX}/admin/users/",
        json={
            "name": "Created By Admin",
            "email": "created@example.com",
            "password": "StrongPassword123!",
            "role": "member",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    assert response.json()["email"] == "created@example.com"


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
def test_admin_list_users(client, admin_headers):
    """An admin can list users with pagination metadata."""
    response = client.get(
        f"{API_PREFIX}/admin/users/",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1  # at least the admin itself


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------
def test_admin_update_user(client, admin_headers):
    """An admin can update another user's data."""
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "Target User",
            "email": "target@example.com",
            "password": "StrongPassword123!",
        },
    )
    user_id = created.json()["id"]

    response = client.patch(
        f"{API_PREFIX}/admin/users/{user_id}",
        json={"name": "Renamed By Admin"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Renamed By Admin"


# ---------------------------------------------------------------------------
# Soft delete
# ---------------------------------------------------------------------------
def test_admin_soft_delete_user(client, admin_headers):
    """An admin can soft delete another user (is_active becomes False)."""
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "To Deactivate",
            "email": "deactivate@example.com",
            "password": "StrongPassword123!",
        },
    )
    user_id = created.json()["id"]

    response = client.delete(
        f"{API_PREFIX}/admin/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_admin_cannot_soft_delete_self(client, admin_headers):
    """An admin cannot deactivate their own account (400)."""
    me = client.get(
        f"{API_PREFIX}/users/me",
        headers=admin_headers,
    ).json()

    response = client.delete(
        f"{API_PREFIX}/admin/users/{me['id']}",
        headers=admin_headers,
    )

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Hard delete
# ---------------------------------------------------------------------------
def test_admin_hard_delete_user(client, admin_headers):
    """An admin can permanently delete another user (204)."""
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "To Delete",
            "email": "delete@example.com",
            "password": "StrongPassword123!",
        },
    )
    user_id = created.json()["id"]

    response = client.delete(
        f"{API_PREFIX}/admin/users/{user_id}/hard",
        headers=admin_headers,
    )

    assert response.status_code == 204


def test_admin_cannot_hard_delete_self(client, admin_headers):
    """An admin cannot permanently delete their own account (400)."""
    me = client.get(
        f"{API_PREFIX}/users/me",
        headers=admin_headers,
    ).json()

    response = client.delete(
        f"{API_PREFIX}/admin/users/{me['id']}/hard",
        headers=admin_headers,
    )

    assert response.status_code == 400
