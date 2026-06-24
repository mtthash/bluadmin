"""Initial schema -- users, roles, permissions, audit_logs with seed data.

Revision ID: 001_initial_schema
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB, UUID

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ── Fixed UUIDs for reproducibility ─────────────────────────────────────────

# Roles
ROLE_HR_ID = "10000000-0000-0000-0000-000000000001"
ROLE_IT_ID = "10000000-0000-0000-0000-000000000002"
ROLE_ADMIN_ID = "10000000-0000-0000-0000-000000000003"

# Permissions
PERM_EMPLOYEE_CREATE_ID = "20000000-0000-0000-0000-000000000001"
PERM_EMPLOYEE_READ_ID = "20000000-0000-0000-0000-000000000002"
PERM_EMPLOYEE_LIST_ID = "20000000-0000-0000-0000-000000000003"
PERM_EMPLOYEE_DISABLE_ID = "20000000-0000-0000-0000-000000000004"
PERM_DEPARTMENT_READ_ID = "20000000-0000-0000-0000-000000000005"
PERM_AUDIT_READ_ID = "20000000-0000-0000-0000-000000000006"
PERM_USER_MANAGE_ID = "20000000-0000-0000-0000-000000000007"


def upgrade() -> None:
    # ── 1. Create tables ────────────────────────────────────────────────

    # -- users --
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("ad_username", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("user_principal_name", sa.String(255), nullable=False),
        sa.Column("job_title", sa.String(255), nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("department_group_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("disabled_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("disabled_at", TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index("ix_users_ad_username", "users", ["ad_username"], unique=True)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_user_principal_name", "users", ["user_principal_name"], unique=True)
    op.create_index("ix_users_status", "users", ["status"])

    # -- roles --
    op.create_table(
        "roles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("ad_group_dn", sa.String(255), unique=True, nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # -- permissions --
    op.create_table(
        "permissions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("codename", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
    )

    # -- role_permissions (many-to-many) --
    op.create_table(
        "role_permissions",
        sa.Column(
            "role_id",
            UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "permission_id",
            UUID(as_uuid=True),
            sa.ForeignKey("permissions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    # -- user_roles --
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "role_id",
            UUID(as_uuid=True),
            sa.ForeignKey("roles.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("assigned_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("assigned_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
    )

    # -- audit_logs --
    op.create_table(
        "audit_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("actor_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_email", sa.String(255), nullable=False),
        sa.Column("target_user_id", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("target_email", sa.String(255), nullable=True),
        sa.Column("details", JSONB, nullable=True),
        sa.Column("result", sa.String(20), nullable=False),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # ── 2. Seed roles ───────────────────────────────────────────────────

    roles_table = sa.table(
        "roles",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )

    op.bulk_insert(
        roles_table,
        [
            {"id": ROLE_HR_ID, "name": "HR", "description": "Human Resources team"},
            {"id": ROLE_IT_ID, "name": "IT", "description": "Information Technology team"},
            {"id": ROLE_ADMIN_ID, "name": "Admin", "description": "System administrators"},
        ],
    )

    # ── 3. Seed permissions ─────────────────────────────────────────────

    permissions_table = sa.table(
        "permissions",
        sa.column("id", UUID(as_uuid=True)),
        sa.column("codename", sa.String),
        sa.column("description", sa.String),
    )

    op.bulk_insert(
        permissions_table,
        [
            {
                "id": PERM_EMPLOYEE_CREATE_ID,
                "codename": "employee:create",
                "description": "Create (onboard) new employees",
            },
            {
                "id": PERM_EMPLOYEE_READ_ID,
                "codename": "employee:read",
                "description": "View individual employee details",
            },
            {
                "id": PERM_EMPLOYEE_LIST_ID,
                "codename": "employee:list",
                "description": "List all employees",
            },
            {
                "id": PERM_EMPLOYEE_DISABLE_ID,
                "codename": "employee:disable",
                "description": "Disable (offboard) employees",
            },
            {
                "id": PERM_DEPARTMENT_READ_ID,
                "codename": "department:read",
                "description": "View departments",
            },
            {
                "id": PERM_AUDIT_READ_ID,
                "codename": "audit:read",
                "description": "View audit logs",
            },
            {
                "id": PERM_USER_MANAGE_ID,
                "codename": "user:manage",
                "description": "Manage user accounts and roles",
            },
        ],
    )

    # ── 4. Seed role_permissions mapping ────────────────────────────────

    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", UUID(as_uuid=True)),
        sa.column("permission_id", UUID(as_uuid=True)),
    )

    # HR: employee:create, employee:read, employee:list, department:read
    hr_permissions = [
        {"role_id": ROLE_HR_ID, "permission_id": PERM_EMPLOYEE_CREATE_ID},
        {"role_id": ROLE_HR_ID, "permission_id": PERM_EMPLOYEE_READ_ID},
        {"role_id": ROLE_HR_ID, "permission_id": PERM_EMPLOYEE_LIST_ID},
        {"role_id": ROLE_HR_ID, "permission_id": PERM_DEPARTMENT_READ_ID},
    ]

    # IT: employee:create, employee:read, employee:list, employee:disable, department:read
    it_permissions = [
        {"role_id": ROLE_IT_ID, "permission_id": PERM_EMPLOYEE_CREATE_ID},
        {"role_id": ROLE_IT_ID, "permission_id": PERM_EMPLOYEE_READ_ID},
        {"role_id": ROLE_IT_ID, "permission_id": PERM_EMPLOYEE_LIST_ID},
        {"role_id": ROLE_IT_ID, "permission_id": PERM_EMPLOYEE_DISABLE_ID},
        {"role_id": ROLE_IT_ID, "permission_id": PERM_DEPARTMENT_READ_ID},
    ]

    # Admin: ALL permissions
    admin_permissions = [
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_EMPLOYEE_CREATE_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_EMPLOYEE_READ_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_EMPLOYEE_LIST_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_EMPLOYEE_DISABLE_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_DEPARTMENT_READ_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_AUDIT_READ_ID},
        {"role_id": ROLE_ADMIN_ID, "permission_id": PERM_USER_MANAGE_ID},
    ]

    op.bulk_insert(
        role_permissions_table,
        hr_permissions + it_permissions + admin_permissions,
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
