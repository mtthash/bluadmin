"""PlatformUser ORM model -- maps to the ``platform_users`` table.

These are the users who log into the BluAdmin platform itself.
Completely separate from AD/employee users.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, String, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PlatformUser(Base):
    __tablename__ = "platform_users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="viewer"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        server_default=text("now()"), onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<PlatformUser {self.username!r} role={self.role!r}>"
