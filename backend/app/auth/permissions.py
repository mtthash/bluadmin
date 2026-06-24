"""Role-based permission definitions and resolution.

Roles map to the platform_users.role field:
  - "Admin" (from role "admin") = full access
  - "Viewer" (from role "viewer") = read-only access
"""

from __future__ import annotations

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Viewer": [
        "employee:read",
        "employee:list",
        "department:read",
        "audit:read",
    ],
    "Admin": [
        "employee:create",
        "employee:read",
        "employee:list",
        "employee:disable",
        "department:read",
        "audit:read",
        "user:manage",
    ],
}


def resolve_permissions(roles: list[str]) -> list[str]:
    permissions: set[str] = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))
    return sorted(permissions)


def check_permissions(user_permissions: list[str], required: list[str]) -> bool:
    return set(required).issubset(set(user_permissions))
