"""AuditLog ORM model -- maps to the ``audit_logs`` table."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import ForeignKey, String, Text, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    # ── Primary key ──────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Action ───────────────────────────────────────────────────────────
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # ── Actor ────────────────────────────────────────────────────────────
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)

    # ── Target ───────────────────────────────────────────────────────────
    target_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    target_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Payload ──────────────────────────────────────────────────────────
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Request context ──────────────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # ── Timestamps ───────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"), index=True
    )

    # ── Relationships ────────────────────────────────────────────────────
    actor: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[actor_id],
        back_populates="audit_logs_as_actor",
        lazy="selectin",
    )
    target_user: Mapped["User | None"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[target_user_id],
        back_populates="audit_logs_as_target",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action!r} by={self.actor_email!r}>"
