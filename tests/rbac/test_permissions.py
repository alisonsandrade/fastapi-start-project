"""Tests for RBAC: roles, permissions and the require_permission guard."""
from sqlalchemy import select

from app.rbac.seed import get_role_by_name
from app.users.models import UserModel
from tests.conftest import API_PREFIX, TestingSessionLocal


# --- Seed / permissions --------------------------------------------------

def test_seed_creates_builtin_roles(client):
    db = TestingSessionLocal()
    try:
        assert get_role_by_name(db, "admin") is not None
        assert get_role_by_name(db, "user") is not None
    finally:
        db.close()


def test_admin_has_users_list_permission(client, admin_user):
    db = TestingSessionLocal()
    try:
        admin = db.execute(
            select(UserModel).where(UserModel.email == admin_user["email"])
        ).scalar_one()
        assert admin.has_permission("users.list") is True
    finally:
        db.close()


def test_user_lacks_users_list_permission(client, registered_user):
    db = TestingSessionLocal()
    try:
        user = db.execute(
            select(UserModel).where(UserModel.email == registered_user["email"])
        ).scalar_one()
        assert user.has_permission("users.list") is False
    finally:
        db.close()


# --- The guard in action (would have caught the dependencies bug) --------

def test_user_forbidden_on_admin_list(client, auth_headers):
    response = client.get(f"{API_PREFIX}/admin/users/", headers=auth_headers)
    assert response.status_code == 403


def test_admin_allowed_on_admin_list(client, admin_headers):
    response = client.get(f"{API_PREFIX}/admin/users/", headers=admin_headers)
    assert response.status_code == 200


def test_unauthenticated_gets_401(client):
    response = client.get(f"{API_PREFIX}/admin/users/")
    assert response.status_code == 401


def test_admin_can_create_role(
    client,
    admin_headers,
):
    response = client.post(
        f"{API_PREFIX}/admin/roles",
        headers=admin_headers,
        json={
            "name": "coordinator",
            "description": "Regional coordinator",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "coordinator"
    assert data["is_system"] is False


def test_member_cannot_create_role(
    client,
    auth_headers,
):
    response = client.post(
        f"{API_PREFIX}/admin/roles",
        headers=auth_headers,
        json={
            "name": "coordinator",
        },
    )

    assert response.status_code == 403


def test_duplicate_role_returns_409(
    client,
    admin_headers,
):
    client.post(
        f"{API_PREFIX}/admin/roles",
        headers=admin_headers,
        json={
            "name": "coordinator",
        },
    )

    response = client.post(
        f"{API_PREFIX}/admin/roles",
        headers=admin_headers,
        json={
            "name": "coordinator",
        },
    )

    assert response.status_code == 409
