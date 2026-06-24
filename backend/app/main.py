"""BluAdmin API -- FastAPI application entry point."""

import asyncio
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


def _bootstrap_ad_groups() -> None:
    """Ensure BluAdmin role groups exist in Active Directory."""
    settings = get_settings()
    if settings.dev_auth_bypass:
        return

    try:
        from app.integrations.ldap.groups import ensure_group_exists
        ensure_group_exists("BluAdmin-HR", "BluAdmin - Human Resources")
        ensure_group_exists("BluAdmin-IT", "BluAdmin - Information Technology")
        ensure_group_exists("BluAdmin-Admin", "BluAdmin - Administrators")
        logger.info("ad_groups_bootstrapped")
    except Exception as exc:
        logger.warning("ad_groups_bootstrap_failed", error=str(exc))


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    setup_logging(
        log_level=settings.log_level,
        json_output=settings.environment == "production",
    )
    logger.info(
        "starting_application",
        environment=settings.environment,
        log_level=settings.log_level,
    )

    session_manager.init(settings.database_url)
    logger.info("database_session_manager_initialised")

    init_role_mapping()
    logger.info("role_mapping_initialised")

    _bootstrap_ad_groups()

    from app.services.deletion_scheduler import run_deletion_scheduler
    deletion_task = asyncio.create_task(run_deletion_scheduler(check_interval=60))

    yield

    deletion_task.cancel()

    await session_manager.close()
    logger.info("application_shutdown_complete")


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()

    application = FastAPI(
        title="BluAdmin API",
        version="1.0.0",
        description="Employee management system integrated with Active Directory",
        docs_url=settings.docs_url,
        openapi_url=settings.openapi_url,
        redoc_url="/redoc" if settings.environment != "production" else None,
        lifespan=lifespan,
    )

    application.add_middleware(StructuredLoggingMiddleware)
    application.add_middleware(SecurityHeadersMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    register_exception_handlers(application)
    application.include_router(api_v1_router, prefix="/api/v1")

    return application


app = create_app()
