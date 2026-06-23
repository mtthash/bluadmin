"""UserRole association model -- maps to the ``user_roles`` table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, text
from sqlalchemy.dialects.postgresql import TIMESTAMPTZ, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    # ── Composite primary key ────────────────────────────────────────────
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # ── Metadata ─────────────────────────────────────────────────────────
    assigned_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default=text("now()")
    )
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # ── Relationships ────────────────────────────────────────────────────
    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[user_id],
        back_populates="roles",
        lazy="selectin",
    )
    role: Mapped["Role"] = relationship(  # noqa: F821
        "Role",
        foreign_keys=[role_id],
        back_populates="user_roles",
        lazy="selectin",
    )
    assigner: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[assigned_by],
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<UserRole user={self.user_id!r} role={self.role_id!r}>"
