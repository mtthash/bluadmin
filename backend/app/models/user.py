"""User ORM model -- maps to the ``users`` table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    # ── Primary key ──────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Identity (synced from Microsoft Entra ID) ────────────────────────
    ad_username: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    user_principal_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    # ── Profile ──────────────────────────────────────────────────────────
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department_group_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    department_rel: Mapped["Department | None"] = relationship(  # noqa: F821
        "Department",
        foreign_keys=[department_id],
        lazy="selectin",
    )

    # ── Status ───────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", index=True
    )

    # ── Audit foreign keys (self-referential) ────────────────────────────
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    disabled_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("now()"),
        onupdate=datetime.utcnow,
    )
    disabled_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    scheduled_deletion_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────────
    creator: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[created_by],
        remote_side="User.id",
        lazy="selectin",
    )
    disabler: Mapped[User | None] = relationship(
        "User",
        foreign_keys=[disabled_by],
        remote_side="User.id",
        lazy="selectin",
    )
    roles: Mapped[list["UserRole"]] = relationship(  # noqa: F821
        "UserRole",
        foreign_keys="UserRole.user_id",
        back_populates="user",
        lazy="selectin",
    )
    audit_logs_as_actor: Mapped[list["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog",
        foreign_keys="AuditLog.actor_id",
        back_populates="actor",
        lazy="noload",
    )
    audit_logs_as_target: Mapped[list["AuditLog"]] = relationship(  # noqa: F821
        "AuditLog",
        foreign_keys="AuditLog.target_user_id",
        back_populates="target_user",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<User {self.email!r} status={self.status!r}>"
