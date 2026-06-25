"""Create departments table and add department_id FK to users.

Revision ID: 004_departments_table
Revises: 003_scheduled_deletion
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "004_departments_table"
down_revision: Union[str, None] = "003_scheduled_deletion"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("mail", sa.String(255), nullable=True),
        sa.Column("ad_group_dn", sa.String(500), unique=True, nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_departments_name", "departments", ["name"], unique=True)

    op.add_column(
        "users",
        sa.Column(
            "department_id",
            UUID(as_uuid=True),
            sa.ForeignKey("departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_users_department_id", "users", ["department_id"])


def downgrade() -> None:
    op.drop_index("ix_users_department_id", "users")
    op.drop_column("users", "department_id")
    op.drop_index("ix_departments_name", "departments")
    op.drop_table("departments")
