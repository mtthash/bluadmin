"""Pydantic schemas for department-related payloads."""

from __future__ import annotations

from pydantic import BaseModel


class DepartmentRead(BaseModel):
    """Read-only representation of an Azure AD / Entra ID group used as a
    department."""

    id: str
    display_name: str
    description: str | None = None
    mail: str | None = None
