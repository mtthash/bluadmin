"""Pydantic schemas for folder mapping payloads."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_DRIVE_RE = re.compile(r"^[A-Z]:$")


class FolderMappingRead(BaseModel):
    id: str
    folder_name: str
    drive_letter: str
    unc_path: str
    is_default: bool
    created_at: datetime


class FolderMappingCreate(BaseModel):
    folder_name: str = Field(..., min_length=1, max_length=255)
    drive_letter: str = Field(..., min_length=2, max_length=3)

    @field_validator("drive_letter")
    @classmethod
    def validate_drive_letter(cls, v: str) -> str:
        v = v.upper().strip()
        if not _DRIVE_RE.match(v):
            raise ValueError("Drive letter must be in format 'X:' (A-Z)")
        return v
