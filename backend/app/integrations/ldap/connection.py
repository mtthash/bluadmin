"""LDAP connection management for on-premises Active Directory."""

from __future__ import annotations

from typing import Any

import ssl

import ldap3
from ldap3 import ALL, Connection, Server, Tls
from ldap3.core.exceptions import LDAPBindError, LDAPException

from app.config import get_settings

_server: Server | None = None


def get_server() -> Server:
    global _server  # noqa: PLW0603
    if _server is None:
        settings = get_settings()
        tls_config = None
        if settings.ldap_use_ssl:
            tls_config = Tls(validate=ssl.CERT_NONE)
        _server = Server(
            settings.ldap_server,
            port=settings.ldap_port,
            use_ssl=settings.ldap_use_ssl,
            tls=tls_config,
            get_info=ALL,
            connect_timeout=10,
        )
    return _server


def get_service_connection() -> Connection:
    settings = get_settings()
    conn = Connection(
        get_server(),
        user=settings.ldap_bind_dn,
        password=settings.ldap_bind_password,
        auto_bind=True,
        raise_exceptions=True,
    )
    return conn


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    """Authenticate a user via LDAP bind and return their attributes."""
    settings = get_settings()
    upn = f"{username}@{settings.ldap_domain}"

    try:
        conn = Connection(
            get_server(),
            user=upn,
            password=password,
            auto_bind=True,
        )
    except (LDAPBindError, LDAPException):
        return None

    try:
        conn.search(
            search_base=settings.ldap_base_dn,
            search_filter=f"(&(objectClass=user)(sAMAccountName={ldap3.utils.conv.escape_filter_chars(username)}))",
            attributes=[
                "distinguishedName",
                "sAMAccountName",
                "displayName",
                "mail",
                "userPrincipalName",
                "memberOf",
                "title",
                "department",
                "objectGUID",
                "userAccountControl",
            ],
        )

        if not conn.entries:
            return None

        entry = conn.entries[0]
        return {
            "dn": str(entry.entry_dn),
            "sAMAccountName": str(entry.sAMAccountName) if entry.sAMAccountName else username,
            "displayName": str(entry.displayName) if entry.displayName else username,
            "mail": str(entry.mail) if entry.mail else f"{username}@{settings.ldap_domain}",
            "userPrincipalName": str(entry.userPrincipalName) if entry.userPrincipalName else upn,
            "memberOf": [str(g) for g in entry.memberOf] if entry.memberOf else [],
            "title": str(entry.title) if entry.title else None,
            "department": str(entry.department) if entry.department else None,
            "objectGUID": str(entry.objectGUID) if entry.objectGUID else None,
            "userAccountControl": int(str(entry.userAccountControl)) if entry.userAccountControl else 512,
        }
    finally:
        conn.unbind()
