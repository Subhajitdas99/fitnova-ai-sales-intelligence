from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi.testclient import TestClient

from backend.app.api.dependencies.services import get_call_repository
from backend.app.domain.enums import CallStatus
from backend.main import app


class FakeDashboardRepository:
    def list_calls_for_analytics(self):
        return [
            SimpleNamespace(
                id="call-1",
                customer_name="Acme",
                sales_rep_name="Jordan",
                status=CallStatus.COMPLETED.value,
                completed_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                duration_seconds=180.0,
                overall_score=88.0,
                close_probability=72.0,
                engagement_score=83.0,
                overall_sentiment="positive",
                outcome="follow_up",
                category_score_details=[
                    {"category": "discovery", "score": 86, "confidence": 0.9},
                    {"category": "rapport", "score": 90, "confidence": 0.9},
                    {"category": "objection_handling", "score": 82, "confidence": 0.8},
                    {"category": "compliance", "score": 91, "confidence": 0.8},
                ],
                detected_issues=["Missed budget range."],
                detected_objections=["Budget"],
                coaching_recommendations=["Ask for budget range."],
                coaching_notes="Coach on budget discovery.",
            )
        ]


def test_dashboard_sprint7_endpoints_return_payloads() -> None:
    app.dependency_overrides[get_call_repository] = lambda: FakeDashboardRepository()
    try:
        with TestClient(app) as client:
            executive_response = client.get("/api/v1/dashboard/executive")
            advisors_response = client.get("/api/v1/dashboard/advisors")
            coaching_response = client.get("/api/v1/dashboard/coaching")
            analytics_response = client.get("/api/v1/analytics")
            legacy_analytics_response = client.get("/api/v1/analytics/dashboard")
    finally:
        app.dependency_overrides.clear()

    assert executive_response.status_code == 200
    assert executive_response.json()["average_ai_quality_score"] == 88
    assert advisors_response.status_code == 200
    assert advisors_response.json()[0]["advisor_name"] == "Jordan"
    assert coaching_response.status_code == 200
    assert coaching_response.json()[0]["practice_goal"]
    assert analytics_response.status_code == 200
    assert analytics_response.json()["advisor_leaderboard"][0]["average_ai_score"] == 88
    assert legacy_analytics_response.status_code == 200
