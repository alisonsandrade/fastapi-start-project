"""Tests for POST /auth/logout."""

from tests.conftest import API_PREFIX


def test_logout_success(client, auth_headers):
    """An authenticated user can log out (204 No Content)."""
    response = client.post(
        f"{API_PREFIX}/auth/logout",
        headers=auth_headers,
    )

    assert response.status_code == 204


def test_access_denied_after_logout(client, auth_headers):
    """After logout the session is terminated, so the access token
    is no longer valid even though it has not expired yet."""
    client.post(
        f"{API_PREFIX}/auth/logout",
        headers=auth_headers,
    )

    response = client.get(
        f"{API_PREFIX}/users/me",
        headers=auth_headers,
    )

    assert response.status_code == 401


def test_logout_without_token(client):
    """Logging out without a token returns 401."""
    response = client.post(f"{API_PREFIX}/auth/logout")

    assert response.status_code == 401
