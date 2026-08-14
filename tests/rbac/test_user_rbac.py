# tests/users/test_user_rbac.py

from tests.conftest import API_PREFIX


def test_admin_can_get_user_rbac(
    client,
    admin_headers,
):
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "RBAC User",
            "email": "rbac@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert created.status_code == 201

    user_id = created.json()["id"]

    response = client.get(
        f"{API_PREFIX}/admin/users/{user_id}/rbac",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == user_id
    assert data["role_name"] == "user"
    assert "permissions" in data
    assert isinstance(data["permissions"], list)


def test_get_user_rbac_not_found(
    client,
    admin_headers,
):
    response = client.get(
        f"{API_PREFIX}/admin/users/not-found/rbac",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_member_cannot_get_user_rbac(
    client,
    auth_headers,
):
    me = client.get(
        f"{API_PREFIX}/users/me",
        headers=auth_headers,
    )

    user_id = me.json()["id"]

    response = client.get(
        f"{API_PREFIX}/admin/users/{user_id}/rbac",
        headers=auth_headers,
    )

    assert response.status_code == 403


def test_rbac_contains_role_information(
    client,
    admin_headers,
):
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "Role Check",
            "email": "rolecheck@example.com",
            "password": "StrongPassword123!",
        },
    )

    user_id = created.json()["id"]

    response = client.get(
        f"{API_PREFIX}/admin/users/{user_id}/rbac",
        headers=admin_headers,
    )

    data = response.json()

    assert "role_id" in data
    assert "role_name" in data
