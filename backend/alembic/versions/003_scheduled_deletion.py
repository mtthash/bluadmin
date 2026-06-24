"""Add scheduled_deletion_at to users.

Revision ID: 003_scheduled_deletion
Revises: 002_platform_users
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003_scheduled_deletion"
down_revision: Union[str, None] = "002_platform_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("scheduled_deletion_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "scheduled_deletion_at")
