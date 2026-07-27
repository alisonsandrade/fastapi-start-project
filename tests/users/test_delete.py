"""Tests for DELETE /users/me (self soft delete)."""

from tests.conftest import API_PREFIX


def test_delete_my_account(client, auth_headers):
    """A user can deactivate (soft delete) their own account."""
    response = client.delete(
        f"{API_PREFIX}/users/me",
        headers=auth_headers,
    )

    # The route soft-deletes and returns the (now inactive) user.
    assert response.status_code == 200


def test_delete_my_account_unauthorized(client):
    """Deleting the account without a token returns 401."""
    response = client.delete(f"{API_PREFIX}/users/me")

    assert response.status_code == 401
