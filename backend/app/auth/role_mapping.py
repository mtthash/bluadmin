"""Map Active Directory group DNs to application role names."""

from __future__ import annotations

from app.config import get_settings

GROUP_DN_TO_ROLE: dict[str, str] = {}


def init_role_mapping() -> None:
    """Build the group-DN-to-role mapping from settings.

    The group DNs are constructed from the domain's base DN.
    Called once during application startup.
    """
    settings = get_settings()
    base = settings.ldap_base_dn

    GROUP_DN_TO_ROLE.clear()
    GROUP_DN_TO_ROLE.update({
        f"CN=BluAdmin-HR,{base}": "HR",
        f"CN=BluAdmin-IT,{base}": "IT",
        f"CN=BluAdmin-Admin,{base}": "Admin",
    })


def resolve_roles_from_groups(group_dns: list[str]) -> list[str]:
    return [
        GROUP_DN_TO_ROLE[dn]
        for dn in group_dns
        if dn in GROUP_DN_TO_ROLE
    ]
