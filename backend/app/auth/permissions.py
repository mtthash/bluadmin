"""Role-based permission definitions and resolution.

Each application role maps to a fixed set of permission codenames.
At request time the user's roles are resolved to a flat, deduplicated
permission list that downstream dependencies use for access control.
"""

from __future__ import annotations

# ── Role -> permissions ─────────────────────────────────────────────────────
ROLE_PERMISSIONS: dict[str, list[str]] = {
    "HR": [
        "employee:create",
        "employee:read",
        "employee:list",
        "department:read",
    ],
    "IT": [
        "employee:create",
        "employee:read",
        "employee:list",
        "employee:disable",
        "department:read",
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
    """Given a list of role names, return a deduplicated list of permissions.

    Roles that are not present in ``ROLE_PERMISSIONS`` are silently
    skipped so that unexpected roles do not cause errors.
    """
    permissions: set[str] = set()
    for role in roles:
        permissions.update(ROLE_PERMISSIONS.get(role, []))
    return sorted(permissions)


def check_permissions(user_permissions: list[str], required: list[str]) -> bool:
    """Return ``True`` if the user possesses ALL required permissions."""
    return set(required).issubset(set(user_permissions))
