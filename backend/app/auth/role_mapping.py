"""Map Azure AD group Object IDs to application role names.

The mapping is initialised once from ``Settings`` and then used at
request time to convert the ``groups`` claim in the JWT to local roles.
"""

from __future__ import annotations

from app.config import get_settings

# ── Group OID -> role name ──────────────────────────────────────────────────
GROUP_TO_ROLE: dict[str, str] = {}


def init_role_mapping() -> None:
    """Populate ``GROUP_TO_ROLE`` from application settings.

    Call this once during application startup (e.g. in a lifespan hook).
    """
    settings = get_settings()

    GROUP_TO_ROLE.clear()
    GROUP_TO_ROLE.update(
        {
            settings.azure_group_id_hr: "HR",
            settings.azure_group_id_it: "IT",
            settings.azure_group_id_admin: "Admin",
        }
    )


def resolve_roles_from_groups(group_ids: list[str]) -> list[str]:
    """Convert a list of Azure AD group OIDs to application role names.

    Unknown group IDs are silently ignored so that users who belong to
    groups outside the role mapping do not cause errors.
    """
    return [
        GROUP_TO_ROLE[gid]
        for gid in group_ids
        if gid in GROUP_TO_ROLE
    ]
