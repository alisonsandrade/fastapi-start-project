"""Seed of built-in roles and permissions (idempotent)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.rbac.models import PermissionModel, RoleModel, RolePermissionModel
from app.rbac.permissions import ALL_PERMISSIONS, BUILTIN_ROLES


def seed_rbac(db: Session) -> None:
    # 1) permissões
    existing_perms = {
        p.code: p for p in db.execute(select(PermissionModel)).scalars()
    }
    for code, desc in ALL_PERMISSIONS:
        if code not in existing_perms:
            perm = PermissionModel(code=code, description=desc)
            db.add(perm)
            existing_perms[code] = perm
    db.flush()

    # 2) roles + associações
    for role_name, cfg in BUILTIN_ROLES.items():
        role = db.execute(
            select(RoleModel).where(RoleModel.name == role_name)
        ).scalar_one_or_none()
        if role is None:
            role = RoleModel(
                name=role_name, description=cfg["description"], is_system=True,
            )
            db.add(role)
            db.flush()

        # resolve as permissões do role
        if cfg["permissions"] == "*":
            perms = list(existing_perms.values())
        else:
            perms = [existing_perms[c] for c in cfg["permissions"]]

        # associa (evitando duplicar)
        current = {
            rp.permission_id
            for rp in db.execute(
                select(RolePermissionModel).where(RolePermissionModel.role_id == role.id)
            ).scalars()
        }
        for perm in perms:
            if perm.id not in current:
                db.add(RolePermissionModel(role_id=role.id, permission_id=perm.id))

    db.commit()


def get_role_by_name(db: Session, name: str) -> RoleModel | None:
    return db.execute(
        select(RoleModel).where(RoleModel.name == name)
    ).scalar_one_or_none()
