"""Re-export every ORM model so Alembic can discover them via Base.metadata."""

from app.models.audit_log import AuditLog
from app.models.platform_user import PlatformUser
from app.models.role import Permission, Role, role_permissions
from app.models.user import User
from app.models.user_role import UserRole

__all__ = [
    "AuditLog",
    "PlatformUser",
    "Permission",
    "Role",
    "User",
    "UserRole",
    "role_permissions",
]
