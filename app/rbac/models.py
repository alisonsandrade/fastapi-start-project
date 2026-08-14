"""RBAC models: roles, permissions and their association"""
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PermissionModel(Base):
    """Uma permissão atômica no formato 'recurso.acao' (ex.: users.delete)"""
    __tablename__ = "permissions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()),
    )
    code: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


class RoleModel(Base):
    """Um papel que agrupa permissões (ex.: admin, user)"""
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4()),
    )
    name: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    # Proteção. Roles de sistema (built-in) não podem ser deletadas pela API
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    permissions: Mapped[list["RolePermissionModel"]] = relationship(
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    @property
    def permission_items(self) -> list["PermissionModel"]:
        return [rp.permission for rp in self.permissions]

    @property
    def permission_count(self) -> int:
        return len(self.permissions)


class RolePermissionModel(Base):
    """Associação N:N entre roles e permissions"""
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission: Mapped["PermissionModel"] = relationship(lazy="joined")
