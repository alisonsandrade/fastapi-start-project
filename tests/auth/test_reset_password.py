"""Tests for POST /auth/reset-password.

Since the token is only returned via log (not via the API response), in the
tests we generate it by calling the service layer directly and then exercise
the public endpoint with that token.
"""

from app.auth import service as auth_service
from tests.conftest import API_PREFIX, TEST_USER, TestingSessionLocal


def _generate_reset_token():
    """Create a real password reset token through the service layer."""
    db = TestingSessionLocal()
    try:
        token = auth_service.request_password_reset(db, TEST_USER["email"])
    finally:
        db.close()
    return token


def test_reset_password_success(client, registered_user):
    """A valid token lets the user set a new password (204)."""
    token = _generate_reset_token()

    response = client.post(
        f"{API_PREFIX}/auth/reset-password",
        json={
            "token": token,
            "new_password": "BrandNewPass123!",
        },
    )

    assert response.status_code == 204


def test_login_works_with_new_password(client, registered_user):
    """After a reset, the user can log in with the NEW password."""
    token = _generate_reset_token()

    client.post(
        f"{API_PREFIX}/auth/reset-password",
        json={
            "token": token,
            "new_password": "BrandNewPass123!",
        },
    )

    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": "BrandNewPass123!",
        },
    )

    assert response.status_code == 200


def test_reset_password_token_cannot_be_reused(client, registered_user):
    """A token can only be used once."""
    token = _generate_reset_token()

    # First use: succeeds.
    client.post(
        f"{API_PREFIX}/auth/reset-password",
        json={
            "token": token,
            "new_password": "BrandNewPass123!",
        },
    )

    # Second use with the same token: rejected.
    response = client.post(
        f"{API_PREFIX}/auth/reset-password",
        json={
            "token": token,
            "new_password": "AnotherPass123!",
        },
    )

    assert response.status_code == 400


def test_reset_password_invalid_token(client, registered_user):
    """An unknown token returns 400."""
    response = client.post(
        f"{API_PREFIX}/auth/reset-password",
        json={
            "token": "invalid-token-value",
            "new_password": "BrandNewPass123!",
        },
    )

    assert response.status_code == 400
