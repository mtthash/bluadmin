"""Azure AD / Microsoft Entra ID token validation.

Fetches the JSON Web Key Set (JWKS) from the Microsoft identity platform,
caches the keys, and validates incoming JWTs against them.

Security notes
--------------
* Only RS256 is accepted -- no algorithm confusion.
* Audience, issuer, and expiration are all verified.
* The JWKS cache refreshes automatically when a ``kid`` is not found
  (key rotation) or when the TTL expires.
"""

from __future__ import annotations

import time
from typing import Any

import httpx
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()

# ── JWKS cache ──────────────────────────────────────────────────────────────
_JWKS_CACHE_TTL_SECONDS = 3600  # 1 hour
_jwks_cache: dict[str, Any] = {}
_jwks_cache_timestamp: float = 0.0

_JWKS_URL = settings.azure_jwks_url
_EXPECTED_AUDIENCE = settings.azure_frontend_client_id
_EXPECTED_ISSUER = f"https://login.microsoftonline.com/{settings.azure_tenant_id}/v2.0"


async def _fetch_jwks() -> dict[str, Any]:
    """Retrieve the JWKS document from the Microsoft identity platform."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(_JWKS_URL)
        response.raise_for_status()
        return response.json()


async def _get_jwks(force_refresh: bool = False) -> dict[str, Any]:
    """Return cached JWKS, refreshing when stale or forced."""
    global _jwks_cache, _jwks_cache_timestamp  # noqa: PLW0603

    now = time.monotonic()
    cache_expired = (now - _jwks_cache_timestamp) > _JWKS_CACHE_TTL_SECONDS

    if not _jwks_cache or cache_expired or force_refresh:
        _jwks_cache = await _fetch_jwks()
        _jwks_cache_timestamp = now

    return _jwks_cache


def _find_rsa_key(jwks: dict[str, Any], kid: str) -> dict[str, str] | None:
    """Find the RSA signing key matching the given key ID."""
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
    return None


async def validate_token(token: str) -> dict[str, Any]:
    """Validate an Azure AD JWT and return its payload claims.

    Raises
    ------
    HTTPException (401)
        If the token is invalid, expired, has a bad audience/issuer, or
        no matching signing key can be found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # ── Decode header (unverified) to get ``kid`` ───────────────────────
    try:
        unverified_header = jwt.get_unverified_header(token)
    except JWTError:
        raise credentials_exception

    kid = unverified_header.get("kid")
    if not kid:
        raise credentials_exception

    # ── Look up the signing key, refreshing cache on miss ───────────────
    jwks = await _get_jwks()
    rsa_key = _find_rsa_key(jwks, kid)

    if rsa_key is None:
        # Key rotation may have occurred -- refresh once and retry.
        jwks = await _get_jwks(force_refresh=True)
        rsa_key = _find_rsa_key(jwks, kid)

    if rsa_key is None:
        raise credentials_exception

    # ── Verify and decode ───────────────────────────────────────────────
    try:
        payload: dict[str, Any] = jwt.decode(
            token,
            rsa_key,
            algorithms=["RS256"],
            audience=_EXPECTED_AUDIENCE,
            issuer=_EXPECTED_ISSUER,
            options={
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_sub": True,
            },
        )
    except JWTError:
        raise credentials_exception

    return payload
