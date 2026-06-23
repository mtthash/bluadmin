"""Security-critical reusable validators.

Every user-facing string MUST pass through one of these annotated types
to prevent SQL injection, XSS, and other injection attacks.
"""

from __future__ import annotations

import re
from typing import Annotated

from pydantic import AfterValidator, EmailStr, Field

# ── Compiled patterns (module-level for performance) ─────────────────────

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_SAFE_NAME_RE = re.compile(r"^[a-zA-ZÀ-ÿ\s'\-\.]+$")
_XSS_PATTERNS = re.compile(
    r"<script|<img|javascript:|on\w+=", re.IGNORECASE
)
_UPN_RE = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)
_HAS_UPPER = re.compile(r"[A-Z]")
_HAS_LOWER = re.compile(r"[a-z]")
_HAS_DIGIT = re.compile(r"\d")
_HAS_SPECIAL = re.compile(r"[^a-zA-Z0-9]")


# ── Validator functions ──────────────────────────────────────────────────


def _validate_safe_name(value: str) -> str:
    """Allow only human names: letters (including accented), spaces, hyphens,
    apostrophes, and dots.  Reject any HTML tags."""
    value = value.strip()
    if not value:
        raise ValueError("Name must not be empty")
    if len(value) > 100:
        raise ValueError("Name must not exceed 100 characters")
    if _HTML_TAG_RE.search(value):
        raise ValueError("Name must not contain HTML tags")
    if not _SAFE_NAME_RE.match(value):
        raise ValueError(
            "Name may only contain letters, spaces, hyphens, "
            "apostrophes, and dots"
        )
    return value


def _validate_safe_string(value: str) -> str:
    """General-purpose safe string: strips whitespace and rejects XSS vectors."""
    value = value.strip()
    if len(value) > 255:
        raise ValueError("Value must not exceed 255 characters")
    if _XSS_PATTERNS.search(value):
        raise ValueError("Value contains potentially dangerous content")
    if _HTML_TAG_RE.search(value):
        raise ValueError("Value must not contain HTML tags")
    return value


def _validate_safe_email(value: str) -> str:
    """Extra guard on top of Pydantic's EmailStr -- reject XSS payloads that
    can sometimes sneak through RFC-compliant parsers."""
    if _XSS_PATTERNS.search(value):
        raise ValueError("Email contains potentially dangerous content")
    if len(value) > 255:
        raise ValueError("Email must not exceed 255 characters")
    return value


def _validate_safe_upn(value: str) -> str:
    """Validate a User Principal Name (user@domain.tld)."""
    value = value.strip()
    if len(value) > 255:
        raise ValueError("UPN must not exceed 255 characters")
    if not _UPN_RE.match(value):
        raise ValueError(
            "UPN must be in the format user@domain.tld with only "
            "alphanumeric characters, dots, underscores, percent signs, "
            "plus signs, and hyphens"
        )
    return value


def _validate_strong_password(value: str) -> str:
    """Enforce a strong password policy: minimum 12 characters with mixed
    character classes."""
    if len(value) < 12:
        raise ValueError("Password must be at least 12 characters long")
    if not _HAS_UPPER.search(value):
        raise ValueError("Password must contain at least one uppercase letter")
    if not _HAS_LOWER.search(value):
        raise ValueError("Password must contain at least one lowercase letter")
    if not _HAS_DIGIT.search(value):
        raise ValueError("Password must contain at least one digit")
    if not _HAS_SPECIAL.search(value):
        raise ValueError(
            "Password must contain at least one special character"
        )
    return value


# ── Annotated types (import these into schemas) ─────────────────────────

SafeName = Annotated[
    str,
    Field(min_length=1, max_length=100),
    AfterValidator(_validate_safe_name),
]

SafeString = Annotated[
    str,
    Field(max_length=255),
    AfterValidator(_validate_safe_string),
]

SafeEmail = Annotated[
    EmailStr,
    AfterValidator(_validate_safe_email),
]

SafeUPN = Annotated[
    str,
    Field(max_length=255),
    AfterValidator(_validate_safe_upn),
]

StrongPassword = Annotated[
    str,
    Field(min_length=12),
    AfterValidator(_validate_strong_password),
]
