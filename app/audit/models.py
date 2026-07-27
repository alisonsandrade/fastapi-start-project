from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AuditLogModel(Base):
    """Audit log model."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    target_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    details: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )