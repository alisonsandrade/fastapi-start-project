"""Tests for GET /users/me and PATCH /users/me."""

from tests.conftest import API_PREFIX, TEST_USER


def test_get_me_success(client, auth_headers):
    """An authenticated user can read their own profile."""
    response = client.get(
        f"{API_PREFIX}/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["email"] == TEST_USER["email"]


def test_get_me_unauthorized(client):
    """Reading /users/me without a token returns 401."""
    response = client.get(f"{API_PREFIX}/users/me")

    assert response.status_code == 401

def test_me_returns_own_data(client, auth_headers, registered_user):
    """GET /users/me retorna os dados do próprio usuário logado."""
    r = client.get(f"{API_PREFIX}/users/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == registered_user["email"]
    assert r.json()["role"] == "user"

def test_update_profile_name(client, auth_headers):
    """The user can update their display name."""
    response = client.patch(
        f"{API_PREFIX}/users/me",
        json={"name": "Updated Name"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"


def test_update_profile_multiple_fields(client, auth_headers):
    """The user can update several profile fields at once."""
    response = client.patch(
        f"{API_PREFIX}/users/me",
        json={
            "phone": "+5575988887777",
            "job_title": "Promotor de Justiça",
            "bio": "Atuação na área criminal.",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["phone"] == "+5575988887777"
    assert data["job_title"] == "Promotor de Justiça"
    assert data["bio"] == "Atuação na área criminal."
