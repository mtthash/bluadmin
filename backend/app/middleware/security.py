"""Security headers middleware.

Adds a comprehensive set of HTTP security headers to every response.
These headers defend against clickjacking, MIME-sniffing, XSS, and
information leakage.  In production the HSTS header is also applied.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.config import get_settings

settings = get_settings()

# Pre-build the CSP value once to avoid per-request string formatting.
_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; "
    "connect-src 'self'; "
    "frame-ancestors 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security-related HTTP headers into every response."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # ── Core security headers ───────────────────────────────────────
        response.headers["Content-Security-Policy"] = _CSP
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
