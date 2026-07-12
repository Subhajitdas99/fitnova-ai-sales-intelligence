from fastapi import APIRouter, Depends

from backend.app.api.dependencies.services import get_analytics_service
from backend.app.application.dto.analytics import AnalyticsDashboardResponse
from backend.app.application.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsDashboardResponse)
def get_analytics(
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsDashboardResponse:
    return service.get_analytics_dashboard()


@router.get("/dashboard", response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    service: AnalyticsService = Depends(get_analytics_service),
) -> AnalyticsDashboardResponse:
    return service.get_analytics_dashboard()
