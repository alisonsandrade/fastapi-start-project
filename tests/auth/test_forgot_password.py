"""Tests for POST /auth/forgot-password.

For security reasons this endpoint ALWAYS returns 204, whether or not the
email exists. This prevents attackers from discovering which emails are
registered in the system (user enumeration).
"""

from tests.conftest import API_PREFIX, TEST_USER


def test_forgot_password_existing_email(client, registered_user):
    """A known email returns 204 No Content."""
    response = client.post(
        f"{API_PREFIX}/auth/forgot-password",
        json={"email": TEST_USER["email"]},
    )

    assert response.status_code == 204


def test_forgot_password_unknown_email(client):
    """An unknown email ALSO returns 204 (no user enumeration)."""
    response = client.post(
        f"{API_PREFIX}/auth/forgot-password",
        json={"email": "ghost@example.com"},
    )

    assert response.status_code == 204
