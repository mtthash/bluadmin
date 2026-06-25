"""Security headers middleware.

Adds a comprehensive set of HTTP security headers to every response.
These headers defend against clickjacking, MIME-sniffing, XSS, and
information leakage.  In production the HSTS header is also applied.
"""

from __future__ import annotations

import base64
import secrets

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings

settings = get_settings()

_DOCS_AUTH_USERNAME = "admin"
_DOCS_AUTH_PASSWORD = "admin"

# Pre-build the CSP value once to avoid per-request string formatting.
_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)


_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")

_DOCS_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://fastapi.tiangolo.com; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)


def _check_basic_auth(request: Request) -> bool:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
        username, password = decoded.split(":", 1)
        return (
            secrets.compare_digest(username, _DOCS_AUTH_USERNAME)
            and secrets.compare_digest(password, _DOCS_AUTH_PASSWORD)
        )
    except Exception:
        return False


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security-related HTTP headers into every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.url.path in _DOCS_PATHS and not _check_basic_auth(request):
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="API Docs"'},
            )

        response = await call_next(request)

        is_docs = request.url.path in _DOCS_PATHS
        # ── Core security headers ───────────────────────────────────────
        response.headers["Content-Security-Policy"] = _DOCS_CSP if is_docs else _CSP
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        # Modern browsers ignore X-XSS-Protection; set to 0 to disable
        # the legacy XSS auditor which can introduce vulnerabilities.
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), payment=()"
        )

        # ── Cache-Control for API responses ─────────────────────────────
        # Prevent caching of API payloads which may contain sensitive data.
        response.headers["Cache-Control"] = "no-store"

        # ── HSTS (production only) ──────────────────────────────────────
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response
