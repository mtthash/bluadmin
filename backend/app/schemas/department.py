"""Pydantic schemas for department-related payloads."""

from __future__ import annotations

from pydantic import BaseModel, Field


class DepartmentRead(BaseModel):
    id: str
    display_name: str
    description: str | None = None
    mail: str | None = None


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
