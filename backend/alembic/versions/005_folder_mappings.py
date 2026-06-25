"""Create folder_mappings table.

Revision ID: 005_folder_mappings
Revises: 004_departments_table
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "005_folder_mappings"
down_revision: Union[str, None] = "004_departments_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "folder_mappings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("folder_name", sa.String(255), nullable=False),
        sa.Column("drive_letter", sa.String(3), nullable=False),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_folder_mappings_user_id", "folder_mappings", ["user_id"])
    op.create_unique_constraint(
        "uq_folder_mappings_user_drive", "folder_mappings", ["user_id", "drive_letter"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_folder_mappings_user_drive", "folder_mappings")
    op.drop_index("ix_folder_mappings_user_id", "folder_mappings")
    op.drop_table("folder_mappings")
