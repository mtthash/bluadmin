"""Create platform_users table with admin seed.

Revision ID: 002_platform_users
Revises: 001_initial_schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import bcrypt as _bcrypt
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002_platform_users"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ADMIN_ID = "a0000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.create_table(
        "platform_users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_platform_users_username", "platform_users", ["username"], unique=True)

    platform_users = sa.table(
        "platform_users",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("display_name", sa.String),
        sa.column("role", sa.String),
        sa.column("is_active", sa.Boolean),
    )

    op.bulk_insert(
        platform_users,
        [
            {
                "id": ADMIN_ID,
                "username": "admin",
                "password_hash": _bcrypt.hashpw(b"admin", _bcrypt.gensalt()).decode(),
                "display_name": "Administrador",
                "role": "admin",
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_table("platform_users")
