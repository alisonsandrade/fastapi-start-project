from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rbac.exceptions import (
    RoleAlreadyExistsError,
    RoleNotFoundError,
    SystemRoleModificationError,
)
from app.rbac.models import PermissionModel, RoleModel


def list_roles(db: Session) -> list[RoleModel]:
    return list(
        db.execute(
            select(RoleModel).order_by(RoleModel.name)
        )
        .scalars()
        .all()
    )


def get_role_by_id(
    db: Session,
    role_id: str,
) -> RoleModel:
    role = db.execute(
        select(RoleModel)
        .where(RoleModel.id == role_id)
    ).scalar_one_or_none()

    if role is None:
        raise RoleNotFoundError("Roles not found.")

    return role


def list_permissions(db: Session) -> list[PermissionModel]:
    return list(
        db.execute(
            select(PermissionModel)
            .order_by(PermissionModel.code)
        ).scalars().all()
    )


def create_role(
    db: Session,
    *,
    name: str,
    description: str | None = None,
) -> RoleModel:
    existing = (
        db.execute(
            select(RoleModel).where(RoleModel.name == name)
        )
        .scalar_one_or_none()
    )

    if (existing):
        raise RoleAlreadyExistsError(f"Role '{name}' already exists.")

    role = RoleModel(
        name=name,
        description=description,
        is_system=False
    )

    db.add(role)
    db.commit()
    db.refresh(role)

    return role


def update_role(
    db: Session,
    role_id: str,
    *,
    description: str | None,
) -> RoleModel:
    role = get_role_by_id(db, role_id)

    if role.is_system:
        raise SystemRoleModificationError("System roles cannot be modified.")

    role.description = description

    db.commit()
    db.refresh(role)

    return role


def delete_role(
    db: Session,
    role_id: str,
) -> None:
    role = get_role_by_id(db, role_id)

    if role.is_system:
        raise SystemRoleModificationError("System roles cannot be modified.")

    db.delete(role)
    db.commit()
