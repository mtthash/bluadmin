"""Pydantic schemas for authentication / authorization payloads."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class TokenPayload(BaseModel):
    """Decoded claims from a Microsoft Entra ID JWT."""

    sub: str
    oid: str
    name: str
    preferred_username: str
    groups: list[str] = Field(default_factory=list)
    aud: str
    iss: str
    exp: int


class CurrentUser(BaseModel):
    """In-memory representation of the currently authenticated user,
    hydrated from the JWT and the local database."""

    id: uuid.UUID
    entra_id: str
    email: str
    display_name: str
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
