"""FolderMapping ORM model -- maps to the ``folder_mappings`` table."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, text
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FolderMapping(Base):
    __tablename__ = "folder_mappings"
    __table_args__ = (
        UniqueConstraint("user_id", "drive_letter", name="uq_folder_mappings_user_drive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    folder_name: Mapped[str] = mapped_column(String(255), nullable=False)
    drive_letter: Mapped[str] = mapped_column(String(3), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        "User",
        foreign_keys=[user_id],
        lazy="noload",
    )

    def __repr__(self) -> str:
        return f"<FolderMapping {self.drive_letter} -> {self.folder_name}>"
