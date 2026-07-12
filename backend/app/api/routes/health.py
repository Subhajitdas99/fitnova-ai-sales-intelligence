from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends, Response, status

from backend.app.core.config import Settings, get_settings
from backend.app.infrastructure.database.session import get_db
from backend.app.schemas.health import (
    ComponentHealth,
    HealthResponse,
    ReadinessResponse,
)

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse, include_in_schema=False)
def health(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(
        status="healthy",
        database="connected",
        version=settings.app_version,
    )


@router.get("/live", response_model=HealthResponse)
def liveness(settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness(
    response: Response,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ReadinessResponse:
    checks = {
        "database": _check_database(db),
        "storage": _check_storage(settings.normalized_storage_dir),
        "openrouter": _check_openrouter(settings),
    }
    ready = all(check.status == "healthy" for check in checks.values())
    if not ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        version=settings.app_version,
        checks=checks,
    )


def _check_database(db: Session) -> ComponentHealth:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return ComponentHealth(status="unhealthy", detail=str(exc))
    return ComponentHealth(status="healthy", detail="Database connection succeeded.")


def _check_storage(storage_dir: Path) -> ComponentHealth:
    try:
        storage_dir.mkdir(parents=True, exist_ok=True)
        if not storage_dir.is_dir():
            return ComponentHealth(
                status="unhealthy", detail="Storage path is not a directory."
            )
        probe = storage_dir / ".healthcheck"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
    except OSError as exc:
        return ComponentHealth(status="unhealthy", detail=str(exc))
    return ComponentHealth(status="healthy", detail="Storage directory is writable.")


def _check_openrouter(settings: Settings) -> ComponentHealth:
    if settings.analysis_provider != "openrouter":
        return ComponentHealth(
            status="healthy", detail="OpenRouter provider is not enabled."
        )
    if not settings.is_openrouter_configured:
        return ComponentHealth(
            status="unhealthy",
            detail="OPENROUTER_API_KEY is not configured.",
        )
    return ComponentHealth(
        status="healthy", detail="OpenRouter configuration is present."
    )
