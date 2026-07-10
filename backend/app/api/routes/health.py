from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi import APIRouter, Depends

from backend.app.core.config import Settings, get_settings
from backend.app.infrastructure.database.session import get_db
from backend.app.schemas.health import HealthResponse


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=HealthResponse)
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
