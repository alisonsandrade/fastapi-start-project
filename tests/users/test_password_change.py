"""Tests for PATCH /users/me/password."""

from tests.conftest import API_PREFIX, TEST_USER


def test_change_password_success(client, auth_headers):
    """A valid current password + strong new password succeeds (200)."""
    response = client.patch(
        f"{API_PREFIX}/users/me/password",
        json={
            "current_password": TEST_USER["password"],
            "new_password": "BrandNewPass123!",
        },
        headers=auth_headers,
    )

    assert response.status_code == 200


def test_change_password_reuse_blocked(client, auth_headers):
    """Reusing the current password is rejected (400)."""
    response = client.patch(
        f"{API_PREFIX}/users/me/password",
        json={
            "current_password": TEST_USER["password"],
            "new_password": TEST_USER["password"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 400


def test_change_password_wrong_current(client, auth_headers):
    """Providing a wrong current password is rejected (401)."""
    response = client.patch(
        f"{API_PREFIX}/users/me/password",
        json={
            "current_password": "TotallyWrong123!",
            "new_password": "BrandNewPass123!",
        },
        headers=auth_headers,
    )

    # Wrong credentials map to 401 via the global exception handler.
    assert response.status_code in (400, 401)


def test_login_works_after_password_change(client, auth_headers):
    """After changing the password, login works with the NEW one."""
    client.patch(
        f"{API_PREFIX}/users/me/password",
        json={
            "current_password": TEST_USER["password"],
            "new_password": "BrandNewPass123!",
        },
        headers=auth_headers,
    )

    response = client.post(
        f"{API_PREFIX}/auth/login",
        data={
            "username": TEST_USER["email"],
            "password": "BrandNewPass123!",
        },
    )

    assert response.status_code == 200
