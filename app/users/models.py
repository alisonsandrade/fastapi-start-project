"""SQLAlchemy model for User (identity and authentication)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.rbac.models import RoleModel


class UserRole:
    """User role constants."""

    ADMIN = "admin"
    USER = "user"

    @classmethod
    def values(cls) -> list:
        return [
            cls.ADMIN,
            cls.USER,
        ]


class UserModel(Base):
    """SQLAlchemy model for application users."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    job_title: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    role: Mapped["RoleModel"] = relationship(lazy="joined")

    @property
    def role_name(self) -> str:
        return self.role.name

    def has_permission(self, code: str) -> bool:
        """True se o role do usuário possui a permissão 'code'"""
        return any(
            rp.permission.code == code
            for rp in self.role.permissions
        )

    @property
    def permissions(self) -> list[str]:
        return [
            rp.permission.code
            for rp in self.role.permissions
        ]

    @property
    def permission_count(self) -> int:
        return len(self.permissions)
