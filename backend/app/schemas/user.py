"""Pydantic schemas for user-related request / response payloads."""

from __future__ import annotations

import re
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import SafeName, SafeString, StrongPassword

# ── Compiled patterns ────────────────────────────────────────────────────

_MAIL_NICKNAME_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._\-]{0,63}$")


class UserCreate(BaseModel):
    """Payload for creating (onboarding) a new user."""

    first_name: SafeName
    last_name: SafeName
    mail_nickname: str = Field(
        ..., min_length=1, max_length=64, examples=["john.doe"]
    )
    password: StrongPassword
    department_group_id: str | None = Field(default=None, max_length=255)
    department_name: SafeString | None = None
    job_title: SafeString | None = None

    @field_validator("mail_nickname")
    @classmethod
    def validate_mail_nickname(cls, v: str) -> str:
        v = v.strip()
        if not _MAIL_NICKNAME_RE.match(v):
            raise ValueError(
                "Mail nickname must start with an alphanumeric character "
                "and may only contain letters, digits, dots, underscores, "
                "and hyphens (max 64 chars)"
            )
        return v


class UserRead(BaseModel):
    """Public representation of a user record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ad_username: str
    display_name: str
    email: str
    user_principal_name: str
    job_title: str | None = None
    department: str | None = None
    department_group_id: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    disabled_at: datetime | None = None
    scheduled_deletion_at: datetime | None = None


class UserList(BaseModel):
    """Paginated list of users."""

    items: list[UserRead]
    total: int
    page: int
    size: int


class OnboardResponse(BaseModel):
    """Response returned after a successful user onboarding."""

    user: UserRead
    temporary_password: str
    status: str
