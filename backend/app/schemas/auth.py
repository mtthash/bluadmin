"""Pydantic schemas for authentication / authorization payloads."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: uuid.UUID
    username: str
    display_name: str
    role: str
    permissions: list[str] = Field(default_factory=list)
