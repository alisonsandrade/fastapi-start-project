"""Tests for POST /auth/register (public user registration)."""

from tests.conftest import API_PREFIX, TEST_USER


def test_register_user_success(client):
    """A valid payload creates a new user user (201)."""
    response = client.post(
        f"{API_PREFIX}/auth/register",
        json=TEST_USER,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    """Registering the same email twice returns 409 Conflict."""
    client.post(f"{API_PREFIX}/auth/register", json=TEST_USER)

    response = client.post(f"{API_PREFIX}/auth/register", json=TEST_USER)

    assert response.status_code == 409


def test_register_weak_password(client):
    """A password that fails the policy returns 422."""
    payload = {
        "name": "Weak Pass",
        "email": "weak@example.com",
        "password": "123456",
    }

    response = client.post(f"{API_PREFIX}/auth/register", json=payload)

    assert response.status_code == 422


def test_register_full_profile(client):
    """Optional profile fields are accepted during registration."""
    payload = {
        "name": "Full Profile",
        "email": "full@example.com",
        "password": "StrongPassword123!",
        "phone": "+5575999999999",
        "job_title": "Promotor de Justiça",
        "bio": "Atuação na área criminal.",
    }

    response = client.post(f"{API_PREFIX}/auth/register", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["phone"] == "+5575999999999"
    assert data["job_title"] == "Promotor de Justiça"
