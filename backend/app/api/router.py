from fastapi import APIRouter

from backend.app.api.routes.analytics import router as analytics_router
from backend.app.api.routes.calls import router as calls_router
from backend.app.api.routes.dashboard import router as dashboard_router
from backend.app.api.routes.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(calls_router)
api_router.include_router(dashboard_router)
api_router.include_router(analytics_router)
