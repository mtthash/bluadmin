"""BluAdmin API -- FastAPI application entry point.

Uses the lifespan pattern (ASGI 3.0) for startup/shutdown lifecycle events.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.auth.role_mapping import init_role_mapping
from app.config import Settings, get_settings
from app.core.logging import setup_logging
from app.db.session import session_manager
from app.middleware.error_handler import register_exception_handlers
from app.middleware.logging_middleware import StructuredLoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware

logger = structlog.stdlib.get_logger("bluadmin.main")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown resources."""
    settings = get_settings()

    # 1. Logging
    setup_logging(
        log_level=settings.log_level,
        json_output=settings.environment == "production",
    )
    logger.info(
        "starting_application",
        environment=settings.environment,
        log_level=settings.log_level,
    )

    # 2. Database
    session_manager.init(settings.database_url)
    logger.info("database_session_manager_initialised")

    # 3. Role mapping (group-id -> role name)
    init_role_mapping()
    logger.info("role_mapping_initialised")

    yield

    # Shutdown
    await session_manager.close()
    logger.info("application_shutdown_complete")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

def create_app(settings: Settings | None = None) -> FastAPI:
    """Build and return the fully configured FastAPI application."""
    if settings is None:
        settings = get_settings()

    application = FastAPI(
        title="BluAdmin API",
        version="1.0.0",
        description="Employee management system integrated with Microsoft Entra ID",
        docs_url=settings.docs_url,
        openapi_url=settings.openapi_url,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    # ── Middleware (applied in reverse order) ─────────────────────────────
    # 1. Structured request/response logging (outermost)
    application.add_middleware(StructuredLoggingMiddleware)

    # 2. Security headers
    application.add_middleware(SecurityHeadersMiddleware)

    # 3. CORS -- restrict to explicit origins only
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    # ── Exception handlers ────────────────────────────────────────────────
    register_exception_handlers(application)

    # ── Routers ───────────────────────────────────────────────────────────
    application.include_router(api_v1_router, prefix="/api/v1")

    return application


# The ASGI application object used by ``uvicorn app.main:app``
app = create_app()
