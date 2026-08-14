from sqlalchemy import select

from tests.conftest import (
    API_PREFIX,
    TestingSessionLocal,
)

from app.rbac.models import RoleModel


def create_role(
    db,
    name: str,
):
    role = RoleModel(
        name=name,
        description=f"{name} role",
        is_system=False,
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def test_admin_can_change_user_role(
    client,
    admin_headers,
):
    db = TestingSessionLocal()

    try:
        role = create_role(
            db,
            "auditor",
        )

        created = client.post(
            f"{API_PREFIX}/auth/register",
            json={
                "name": "Role User",
                "email": "roleuser@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert created.status_code == 201

        user_id = created.json()["id"]

        response = client.patch(
            f"{API_PREFIX}/admin/users/{user_id}/roles",
            json={
                "role_id": role.id,
            },
            headers=admin_headers,
        )

        assert response.status_code == 200

        data = response.json()

        assert data["role"] == "auditor"

    finally:
        db.close()


def test_change_user_role_user_not_found(
    client,
    admin_headers,
):
    db = TestingSessionLocal()

    try:
        role = create_role(
            db,
            "auditor",
        )

        response = client.patch(
            f"{API_PREFIX}/admin/users/00000000-0000-0000-0000-000000000000/roles",
            json={
                "role_id": role.id,
            },
            headers=admin_headers,
        )

        assert response.status_code == 404

    finally:
        db.close()


def test_change_user_role_role_not_found(
    client,
    admin_headers,
):
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "Role User",
            "email": "roleuser2@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert created.status_code == 201

    user_id = created.json()["id"]

    response = client.patch(
        f"{API_PREFIX}/admin/users/{user_id}/roles",
        json={
            "role_id": "not-found-role",
        },
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_member_cannot_change_user_role(
    client,
    auth_headers,
):
    db = TestingSessionLocal()

    try:
        role = create_role(
            db,
            "auditor",
        )

        me = client.get(
            f"{API_PREFIX}/users/me",
            headers=auth_headers,
        )

        user_id = me.json()["id"]

        response = client.patch(
            f"{API_PREFIX}/admin/users/{user_id}/roles",
            json={
                "role_id": role.id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 403

    finally:
        db.close()
