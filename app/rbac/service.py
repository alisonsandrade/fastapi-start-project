from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.rbac.exceptions import (
    RoleAlreadyExistsError,
    RoleInUseError,
    RoleNotFoundError,
    SystemRoleModificationError,
)
from app.rbac.models import PermissionModel, RoleModel
from app.users.models import UserModel
from app.users.service import get_user_by_id


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


def change_user_role(
    db: Session,
    user_id: str,
    role_id: str,
) -> UserModel:
    user = get_user_by_id(db, user_id)

    role = get_role_by_id(db, role_id)

    user.role_id = role.id

    db.commit()
    db.refresh(user)

    return user


def delete_role(
    db: Session,
    role_id: str,
) -> None:
    role = get_role_by_id(db, role_id)

    if role.is_system:
        raise SystemRoleModificationError("System roles cannot be modified.")

    users_count = db.scalar(
        select(func.count()).select_from(UserModel)
        .where(UserModel.role_id == role.id)
    )

    if users_count and users_count > 0:
        raise RoleInUseError(
            f"Role is assigned to {users_count} users and cannot be deleted."
        )

    db.delete(role)
    db.commit()
