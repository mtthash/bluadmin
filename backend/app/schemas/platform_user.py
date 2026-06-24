"""Pydantic schemas for platform user management."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlatformUserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=4)
    display_name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="viewer", pattern="^(admin|viewer)$")


class PlatformUserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=255)
    role: str | None = Field(default=None, pattern="^(admin|viewer)$")
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=4)


class PlatformUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    display_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PlatformUserList(BaseModel):
    items: list[PlatformUserRead]
    total: int
