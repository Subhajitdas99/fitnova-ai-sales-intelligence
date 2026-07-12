from fastapi import APIRouter, Depends

from backend.app.api.dependencies.services import get_dashboard_service
from backend.app.application.dto.analytics import (
    AdvisorPerformanceResponse,
    CoachingCardResponse,
    ExecutiveDashboardResponse,
)
from backend.app.application.services.dashboard_service import DashboardService
from backend.app.schemas.calls import CallListItemResponse, DashboardOverviewResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview(
    service: DashboardService = Depends(get_dashboard_service),
) -> DashboardOverviewResponse:
    payload = service.get_overview()
    return DashboardOverviewResponse(
        total_calls=int(payload["total_calls"]),
        completed_calls=int(payload["completed_calls"]),
        failed_calls=int(payload["failed_calls"]),
        processing_calls=int(payload["processing_calls"]),
        average_close_probability=float(payload["average_close_probability"]),
        average_engagement_score=float(payload["average_engagement_score"]),
        sentiment_breakdown=dict(payload["sentiment_breakdown"]),
        outcome_breakdown=dict(payload["outcome_breakdown"]),
        recent_calls=[
            CallListItemResponse.model_validate(record)
            for record in payload["recent_calls"]
        ],
    )


@router.get("/executive", response_model=ExecutiveDashboardResponse)
def get_executive_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
) -> ExecutiveDashboardResponse:
    return service.get_executive_dashboard()


@router.get("/advisors", response_model=list[AdvisorPerformanceResponse])
def get_advisor_performance(
    service: DashboardService = Depends(get_dashboard_service),
) -> list[AdvisorPerformanceResponse]:
    return service.get_advisor_performance()


@router.get("/coaching", response_model=list[CoachingCardResponse])
def get_coaching_dashboard(
    service: DashboardService = Depends(get_dashboard_service),
) -> list[CoachingCardResponse]:
    return service.get_coaching_dashboard()
