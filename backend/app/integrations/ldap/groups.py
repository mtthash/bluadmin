"""LDAP group operations for Active Directory."""

from __future__ import annotations

from typing import Any

import ldap3
from ldap3 import MODIFY_ADD, MODIFY_DELETE

from app.config import get_settings
from app.core.exceptions import LDAPOperationError
from app.integrations.ldap.connection import get_service_connection


def list_groups(filter_prefix: str | None = None) -> list[dict[str, Any]]:
    settings = get_settings()
    conn = get_service_connection()
    try:
        if filter_prefix:
            escaped = ldap3.utils.conv.escape_filter_chars(filter_prefix)
            search_filter = f"(&(objectClass=group)(cn={escaped}*))"
        else:
            search_filter = "(objectClass=group)"

        conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=search_filter,
            attributes=["distinguishedName", "cn", "description", "mail", "objectGUID"],
        )

        return [
            {
                "dn": str(entry.entry_dn),
                "cn": str(entry.cn) if entry.cn else "",
                "description": str(entry.description) if entry.description else None,
                "mail": str(entry.mail) if entry.mail else None,
                "objectGUID": str(entry.objectGUID) if entry.objectGUID else None,
            }
            for entry in conn.entries
        ]
    finally:
        conn.unbind()


def add_group_member(group_dn: str, user_dn: str) -> None:
    conn = get_service_connection()
    try:
        success = conn.modify(group_dn, {"member": [(MODIFY_ADD, [user_dn])]})
        if not success:
            desc = conn.result.get("description", "Unknown error")
            if "already exists" not in desc.lower() and "entry already exists" not in desc.lower():
                raise LDAPOperationError("add_group_member", desc)
    except LDAPOperationError:
        raise
    except Exception as exc:
        raise LDAPOperationError("add_group_member", str(exc)) from exc
    finally:
        conn.unbind()


def remove_group_member(group_dn: str, user_dn: str) -> None:
    conn = get_service_connection()
    try:
        success = conn.modify(group_dn, {"member": [(MODIFY_DELETE, [user_dn])]})
        if not success:
            desc = conn.result.get("description", "Unknown error")
            if "no such attribute" not in desc.lower():
                raise LDAPOperationError("remove_group_member", desc)
    except LDAPOperationError:
        raise
    except Exception as exc:
        raise LDAPOperationError("remove_group_member", str(exc)) from exc
    finally:
        conn.unbind()


def get_user_groups(user_dn: str) -> list[dict[str, Any]]:
    settings = get_settings()
    escaped = ldap3.utils.conv.escape_filter_chars(user_dn)
    conn = get_service_connection()
    try:
        conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=f"(&(objectClass=group)(member={escaped}))",
            attributes=["distinguishedName", "cn"],
        )
        return [
            {"dn": str(entry.entry_dn), "cn": str(entry.cn) if entry.cn else ""}
            for entry in conn.entries
        ]
    finally:
        conn.unbind()


def ensure_group_exists(group_cn: str, description: str | None = None) -> str:
    """Create a group if it doesn't exist. Returns the DN."""
    settings = get_settings()
    dn = f"CN={group_cn},{settings.ldap_base_dn}"

    conn = get_service_connection()
    try:
        conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=f"(&(objectClass=group)(cn={ldap3.utils.conv.escape_filter_chars(group_cn)}))",
            attributes=["distinguishedName"],
        )
        if conn.entries:
            return str(conn.entries[0].entry_dn)

        attrs = {
            "objectClass": ["top", "group"],
            "cn": group_cn,
            "sAMAccountName": group_cn,
            "groupType": "-2147483646",  # Global security group
        }
        if description:
            attrs["description"] = description

        success = conn.add(dn, attributes=attrs)
        if not success:
            raise LDAPOperationError("ensure_group_exists", conn.result.get("description", "Unknown error"))

        return dn
    except LDAPOperationError:
        raise
    except Exception as exc:
        raise LDAPOperationError("ensure_group_exists", str(exc)) from exc
    finally:
        conn.unbind()
