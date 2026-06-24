"""Local JWT creation and validation for LDAP-based authentication."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.jwt_expiration_minutes)
    )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})

    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def validate_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        raise credentials_exception

    if not payload.get("sub"):
        raise credentials_exception

    return payload
