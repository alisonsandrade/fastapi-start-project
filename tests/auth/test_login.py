"""Tests for POST /auth/login.

Login uses OAuth2PasswordRequestForm, so credentials must be sent as
FORM DATA (data=...), NOT JSON. The `username` field carries the email.
"""

from tests.conftest import API_PREFIX, TEST_USER


def test_login_success(client, registered_user):
    """A valid email/password pair returns access + refresh tokens."""
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"],
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client, registered_user):
    """A wrong password returns 401 Unauthorized."""
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_login_unknown_email(client):
    """An email that does not exist returns 401 (never 404).

    Returning 401 for both cases prevents user enumeration attacks.
    """
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": "ghost@example.com",
            "password": "whatever123",
        },
    )

    assert response.status_code == 401
