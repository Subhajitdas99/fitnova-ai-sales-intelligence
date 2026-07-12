from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from backend.app.api.exception_handlers import register_exception_handlers
from backend.app.api.middleware import (
    RequestContextMiddleware,
    RequestTimeoutMiddleware,
    SecurityHeadersMiddleware,
)
from backend.app.api.router import api_router
from backend.app.api.routes.health import router as health_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging, get_logger
from backend.app.infrastructure.database.initialization import initialize_database

# ==============================================================================
# Configuration
# ==============================================================================

settings = get_settings()

configure_logging(settings.log_level)

logger = get_logger(__name__)


# ==============================================================================
# Application Lifespan
# ==============================================================================


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """
    Initialize application infrastructure during startup and perform
    graceful shutdown when the application exits.
    """

    logger.info("Starting FitNova AI Sales Intelligence...")

    settings.validate_for_startup()

    settings.normalized_storage_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    initialize_database()

    logger.info("Application startup completed successfully.")

    try:
        yield
    finally:
        logger.info("Application shutdown completed.")


# ==============================================================================
# FastAPI Application Factory
# ==============================================================================


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    """

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
        redirect_slashes=False,
    )

    # --------------------------------------------------------------------------
    # Middleware
    #
    # Middleware execution order (request):
    #
    # RequestContext
    # ↓
    # CORS
    # ↓
    # GZip
    # ↓
    # SecurityHeaders
    # ↓
    # RequestTimeout
    # ↓
    # Route Handler
    # --------------------------------------------------------------------------

    app.add_middleware(
        RequestTimeoutMiddleware,
        timeout_seconds=settings.request_timeout_seconds,
    )

    app.add_middleware(SecurityHeadersMiddleware)

    app.add_middleware(
        GZipMiddleware,
        minimum_size=500,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(RequestContextMiddleware)

    # --------------------------------------------------------------------------
    # Exception Handlers
    # --------------------------------------------------------------------------

    register_exception_handlers(app)

    # --------------------------------------------------------------------------
    # Routes
    # --------------------------------------------------------------------------

    app.include_router(health_router)

    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    @app.get("/", tags=["Root"])
    async def root() -> dict[str, str]:
        return {
            "message": settings.app_name,
            "status": "running",
            "version": settings.app_version,
            "docs": "/docs",
        }

    return app


# ==============================================================================
# ASGI Application
# ==============================================================================

app = create_application()
