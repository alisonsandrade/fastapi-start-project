# tests/rbac/test_role_permissions.py

import pytest
from sqlalchemy import select

from tests.conftest import TestingSessionLocal

from app.rbac.exceptions import (
    PermissionAlreadyAssignedError,
    PermissionNotAssignedError,
    PermissionNotFoundError,
    RoleNotFoundError,
    SystemRoleModificationError,
)

from app.rbac.models import (
    PermissionModel,
    RoleModel,
    RolePermissionModel,
)

from app.rbac.role_permissions import (
    add_permission_to_role,
    get_role_permission,
    list_role_permissions,
    remove_permission_from_role,
)


def create_permission(db):
    return db.execute(
        select(PermissionModel)
        .where(PermissionModel.code == "users.list")
    ).scalar_one()


def create_role(db):
    role = RoleModel(
        name="auditor",
        description="Auditor role",
        is_system=False,
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def create_system_role(db):
    return db.execute(
        select(RoleModel)
        .where(RoleModel.name == "admin")
    ).scalar_one()


def test_list_role_permissions(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)
        permission = create_permission(db)

        db.add(
            RolePermissionModel(
                role_id=role.id,
                permission_id=permission.id,
            )
        )
        db.commit()

        result = list_role_permissions(
            db,
            role.id,
        )

        assert len(result) == 1
        assert result[0].id == permission.id
        assert result[0].code == permission.code

    finally:
        db.close()


def test_add_permission_to_role(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)
        permission = create_permission(db)

        add_permission_to_role(
            db,
            role.id,
            permission.id,
        )

        relation = get_role_permission(
            db,
            role.id,
            permission.id,
        )

        assert relation is not None
        assert relation.role_id == role.id
        assert relation.permission_id == permission.id

    finally:
        db.close()


def test_add_permission_to_role_duplicate(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)
        permission = create_permission(db)

        add_permission_to_role(
            db,
            role.id,
            permission.id,
        )

        with pytest.raises(
            PermissionAlreadyAssignedError,
        ):
            add_permission_to_role(
                db,
                role.id,
                permission.id,
            )

    finally:
        db.close()


def test_add_permission_to_role_with_invalid_permission(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)

        with pytest.raises(
            PermissionNotFoundError,
        ):
            add_permission_to_role(
                db,
                role.id,
                "invalid-permission-id",
            )

    finally:
        db.close()


def test_add_permission_to_role_with_invalid_role(client):
    db = TestingSessionLocal()

    try:
        permission = create_permission(db)

        with pytest.raises(
            RoleNotFoundError,
        ):
            add_permission_to_role(
                db,
                "invalid-role-id",
                permission.id,
            )

    finally:
        db.close()


def test_remove_permission_from_role(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)
        permission = create_permission(db)

        add_permission_to_role(
            db,
            role.id,
            permission.id,
        )

        remove_permission_from_role(
            db,
            role.id,
            permission.id,
        )

        relation = get_role_permission(
            db,
            role.id,
            permission.id,
        )

        assert relation is None

    finally:
        db.close()


def test_remove_permission_not_assigned(client):
    db = TestingSessionLocal()

    try:
        role = create_role(db)
        permission = create_permission(db)

        with pytest.raises(
            PermissionNotAssignedError,
        ):
            remove_permission_from_role(
                db,
                role.id,
                permission.id,
            )

    finally:
        db.close()


def test_add_permission_to_system_role(client):
    db = TestingSessionLocal()

    try:
        role = create_system_role(db)
        permission = create_permission(db)

        with pytest.raises(
            SystemRoleModificationError,
        ):
            add_permission_to_role(
                db,
                role.id,
                permission.id,
            )

    finally:
        db.close()


def test_remove_permission_from_system_role(client):
    db = TestingSessionLocal()

    try:
        role = create_system_role(db)
        permission = create_permission(db)

        with pytest.raises(
            SystemRoleModificationError,
        ):
            remove_permission_from_role(
                db,
                role.id,
                permission.id,
            )

    finally:
        db.close()
