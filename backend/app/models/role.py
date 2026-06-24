"""Role and Permission ORM models, plus the role_permissions association table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String, Table, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

# ── Association table: role <-> permission (many-to-many) ────────────────
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ad_group_dn: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    # ── Relationships ────────────────────────────────────────────────────
    permissions: Mapped[list[Permission]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )
    user_roles: Mapped[list["UserRole"]] = relationship(  # noqa: F821
        "UserRole",
        back_populates="role",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Role {self.name!r}>"


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    codename: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<Permission {self.codename!r}>"
