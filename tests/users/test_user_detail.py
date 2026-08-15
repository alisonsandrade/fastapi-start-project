from tests.conftest import API_PREFIX


def test_admin_can_get_user_by_id(
    client,
    admin_headers,
):
    created = client.post(
        f"{API_PREFIX}/auth/register",
        json={
            "name": "Detail User",
            "email": "detail@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert created.status_code == 201

    user_id = created.json()["id"]

    response = client.get(
        f"{API_PREFIX}/admin/users/{user_id}",
        headers=admin_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == user_id
    assert data["email"] == "detail@example.com"
    assert "role" in data
    assert "permissions" in data


def test_get_user_by_id_not_found(
    client,
    admin_headers,
):
    response = client.get(
        f"{API_PREFIX}/admin/users/00000000-0000-0000-0000-000000000000",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_member_cannot_get_user_by_id(
    client,
    auth_headers,
):
    me = client.get(
        f"{API_PREFIX}/users/me",
        headers=auth_headers,
    )

    user_id = me.json()["id"]

    response = client.get(
        f"{API_PREFIX}/admin/users/{user_id}",
        headers=auth_headers,
    )

    assert response.status_code == 403

