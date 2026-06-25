"""LDAP user operations for Active Directory."""

from __future__ import annotations

from typing import Any

import ldap3
from ldap3 import MODIFY_REPLACE

from app.config import get_settings
from app.core.exceptions import LDAPOperationError
from app.integrations.ldap.connection import get_service_connection

import structlog

logger = structlog.get_logger(__name__)


def create_ldap_user(
    display_name: str,
    sam_account_name: str,
    password: str,
    job_title: str | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    dn = f"CN={display_name},{settings.ldap_base_dn}"
    upn = f"{sam_account_name}@{settings.ldap_domain}"

    name_parts = display_name.split(" ", 1)
    given_name = name_parts[0]
    surname = name_parts[1] if len(name_parts) > 1 else name_parts[0]

    attributes = {
        "objectClass": ["top", "person", "organizationalPerson", "user"],
        "sAMAccountName": sam_account_name,
        "userPrincipalName": upn,
        "displayName": display_name,
        "givenName": given_name,
        "sn": surname,
        "mail": upn,
        "userAccountControl": "544",
    }
    if job_title:
        attributes["title"] = job_title

    conn = get_service_connection()
    try:
        success = conn.add(dn, attributes=attributes)
        if not success:
            desc = conn.result.get("description", "Unknown error")
            if "entryAlreadyExists" in str(conn.result):
                logger.info("ldap_user_already_exists", dn=dn)
                existing = search_user(sam_account_name)
                return {
                    "dn": existing["dn"] if existing else dn,
                    "sAMAccountName": sam_account_name,
                    "userPrincipalName": upn,
                    "displayName": display_name,
                    "password_set": False,
                }
            raise LDAPOperationError("create_user", desc)

        password_set = False
        if settings.ldap_use_ssl:
            try:
                conn.extend.microsoft.modify_password(dn, new_password=password)
                conn.modify(dn, {"userAccountControl": [(MODIFY_REPLACE, ["512"])]})
                password_set = True
            except Exception as exc:
                logger.warning("password_set_failed_ssl", error=str(exc))

        if not password_set:
            logger.info(
                "user_created_without_password",
                dn=dn,
                reason="LDAPS required for password operations",
            )

        return {
            "dn": dn,
            "sAMAccountName": sam_account_name,
            "userPrincipalName": upn,
            "displayName": display_name,
            "password_set": password_set,
        }
    except LDAPOperationError:
        raise
    except Exception as exc:
        if "entryAlreadyExists" in str(exc) or "ENTRY_EXISTS" in str(exc):
            logger.info("ldap_user_already_exists", dn=dn)
            conn.unbind()
            existing = search_user(sam_account_name)
            return {
                "dn": existing["dn"] if existing else dn,
                "sAMAccountName": sam_account_name,
                "userPrincipalName": upn,
                "displayName": display_name,
                "password_set": False,
            }
        raise LDAPOperationError("create_user", str(exc)) from exc
    finally:
        conn.unbind()


def delete_ldap_user(user_dn: str) -> None:
    conn = get_service_connection()
    try:
        success = conn.delete(user_dn)
        if not success:
            raise LDAPOperationError("delete_user", conn.result.get("description", "Unknown error"))
    except LDAPOperationError:
        raise
    except Exception as exc:
        raise LDAPOperationError("delete_user", str(exc)) from exc
    finally:
        conn.unbind()


def disable_ldap_user(user_dn: str) -> None:
    conn = get_service_connection()
    try:
        success = conn.modify(user_dn, {"userAccountControl": [(MODIFY_REPLACE, ["514"])]})
        if not success:
            raise LDAPOperationError("disable_user", conn.result.get("description", "Unknown error"))
    except LDAPOperationError:
        raise
    except Exception as exc:
        raise LDAPOperationError("disable_user", str(exc)) from exc
    finally:
        conn.unbind()


def search_user(sam_account_name: str) -> dict[str, Any] | None:
    settings = get_settings()
    conn = get_service_connection()
    try:
        escaped = ldap3.utils.conv.escape_filter_chars(sam_account_name)
        conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=f"(&(objectClass=user)(sAMAccountName={escaped}))",
            attributes=[
                "distinguishedName", "sAMAccountName", "displayName",
                "mail", "userPrincipalName", "memberOf", "title",
                "department", "objectGUID", "userAccountControl",
            ],
        )
        if not conn.entries:
            return None

        entry = conn.entries[0]
        return {
            "dn": str(entry.entry_dn),
            "sAMAccountName": str(entry.sAMAccountName) if entry.sAMAccountName else sam_account_name,
            "displayName": str(entry.displayName) if entry.displayName else "",
            "mail": str(entry.mail) if entry.mail else "",
            "memberOf": [str(g) for g in entry.memberOf] if entry.memberOf else [],
            "userAccountControl": int(str(entry.userAccountControl)) if entry.userAccountControl else 512,
        }
    finally:
        conn.unbind()
