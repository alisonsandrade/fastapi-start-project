"""Tests for POST /auth/refresh (refresh token rotation)."""

from tests.conftest import API_PREFIX, TEST_USER


def _login(client):
    """Helper: log in and return the full token payload."""
    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": TEST_USER["password"],
        },
    )
    return response.json()


def test_refresh_success(client, registered_user):
    """A valid refresh token returns a brand new pair of tokens."""
    tokens = _login(client)

    response = client.post(
        f"{API_PREFIX}/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_invalid_token(client):
    """An unknown refresh token returns 401."""
    response = client.post(
        f"{API_PREFIX}/auth/refresh",
        json={"refresh_token": "x" * 64},
    )

    assert response.status_code == 401


def test_refresh_rotation_revokes_old_token(client, registered_user):
    """After rotation, the OLD refresh token must stop working.

    This is the whole point of "refresh token rotation": reusing a token
    that was already exchanged is treated as invalid.
    """
    tokens = _login(client)
    old_refresh = tokens["refresh_token"]

    # First refresh: succeeds and rotates the token.
    client.post(
        f"{API_PREFIX}/auth/refresh",
        json={"refresh_token": old_refresh},
    )

    # Second refresh with the SAME old token: must fail.
    response = client.post(
        f"{API_PREFIX}/auth/refresh",
        json={"refresh_token": old_refresh},
    )

    assert response.status_code == 401
