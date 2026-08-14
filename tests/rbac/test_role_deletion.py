# tests/rbac/test_role_deletion.py

from sqlalchemy import select

from tests.conftest import (
    API_PREFIX,
    TestingSessionLocal,
)

from app.rbac.models import RoleModel


def create_role(
    db,
    name: str = "auditor",
):
    role = RoleModel(
        name=name,
        description="Auditor role",
        is_system=False,
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def test_delete_unused_role(
    client,
    admin_headers,
):
    db = TestingSessionLocal()

    try:
        role = create_role(db)

        response = client.delete(
            f"{API_PREFIX}/admin/roles/{role.id}",
            headers=admin_headers,
        )

        assert response.status_code == 204

    finally:
        db.close()


def test_delete_role_not_found(
    client,
    admin_headers,
):
    response = client.delete(
        f"{API_PREFIX}/admin/roles/not-found-id",
        headers=admin_headers,
    )

    assert response.status_code == 404


def test_delete_system_role_forbidden(
    client,
    admin_headers,
):
    db = TestingSessionLocal()

    try:
        admin_role = db.execute(
            select(RoleModel)
            .where(RoleModel.name == "admin")
        ).scalar_one()

        response = client.delete(
            f"{API_PREFIX}/admin/roles/{admin_role.id}",
            headers=admin_headers,
        )

        assert response.status_code == 400

    finally:
        db.close()


def test_member_cannot_delete_role(
    client,
    auth_headers,
):
    db = TestingSessionLocal()

    try:
        role = create_role(db)

        response = client.delete(
            f"{API_PREFIX}/admin/roles/{role.id}",
            headers=auth_headers,
        )

        assert response.status_code == 403

    finally:
        db.close()
