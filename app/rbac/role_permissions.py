from sqlalchemy import select
from sqlalchemy.orm.session import Session

from app.rbac.exceptions import PermissionAlreadyAssignedError, PermissionNotAssignedError, PermissionNotFoundError, SystemRoleModificationError
from app.rbac.models import PermissionModel, RolePermissionModel
from app.rbac.service import get_role_by_id


def list_role_permissions(db: Session, role_id: str) -> list:
    role = get_role_by_id(db, role_id)

    return role.permission_items


def get_permissions_by_id(db: Session, permission_id: str) -> PermissionModel:
    permission = db.execute(
        select(PermissionModel)
        .where(PermissionModel.id == permission_id)
    ).scalar_one_or_none()

    if permission is None:
        raise PermissionNotFoundError(
            "Permission not found."
        )

    return permission


def add_permission_to_role(
    db: Session,
    role_id: str,
    permission_id: str,
) -> None:
    role = get_role_by_id(db, role_id)

    permission = get_permissions_by_id(db, permission_id)

    if role.is_system:
        raise SystemRoleModificationError(
            "System roles cannot be modified."
        )

    if get_role_permission(db, role_id, permission_id):
        raise PermissionAlreadyAssignedError(
            "Permission already assingned to role."
        )

    db.add(
        RolePermissionModel(
            role_id=role.id,
            permission_id=permission.id,
        )
    )

    db.commit()


def remove_permission_from_role(
    db: Session,
    role_id: str,
    permission_id: str,
) -> None:
    role = get_role_by_id(db, role_id)

    if role.is_system:
        raise SystemRoleModificationError(
            "System roles cannot be modified."
        )

    role_permission = get_role_permission(
        db,
        role_id,
        permission_id
    )

    if role_permission is None:
        raise PermissionNotAssignedError(
            "Permission not assigned to role."
        )

    db.delete(role_permission)

    db.commit()


def get_role_permission(
    db: Session,
    role_id: str,
    permission_id: str,
) -> RolePermissionModel | None:
    return db.execute(
        select(RolePermissionModel)
        .where(
            RolePermissionModel.role_id == role_id,
            RolePermissionModel.permission_id == permission_id,
        )
    ).scalar_one_or_none()
