from datetime import datetime, timezone
from types import SimpleNamespace

from backend.app.application.services.analytics_service import AnalyticsService
from backend.app.application.services.dashboard_service import DashboardService
from backend.app.domain.enums import CallStatus


def make_call(
    call_id: str,
    advisor: str,
    ai_score: float,
    close_probability: float,
    sentiment: str,
    outcome: str,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=call_id,
        customer_name=f"Customer {call_id}",
        sales_rep_name=advisor,
        status=CallStatus.COMPLETED.value,
        completed_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        duration_seconds=120.0,
        overall_score=ai_score,
        close_probability=close_probability,
        engagement_score=ai_score - 5,
        overall_sentiment=sentiment,
        outcome=outcome,
        category_score_details=[
            {"category": "discovery", "score": ai_score - 2, "confidence": 0.9},
            {
                "category": "objection_handling",
                "score": ai_score - 4,
                "confidence": 0.8,
            },
            {"category": "rapport", "score": ai_score - 1, "confidence": 0.8},
            {"category": "compliance", "score": ai_score - 3, "confidence": 0.8},
        ],
        detected_issues=["Pricing was not quantified."],
        detected_objections=["Pricing"],
        coaching_recommendations=["Ask for budget range."],
        coaching_notes="Good rapport; improve pricing discovery.",
    )


class FakeAnalyticsRepository:
    def __init__(self) -> None:
        self.calls = [
            make_call("call-1", "Jordan", 90, 80, "positive", "follow_up"),
            make_call("call-2", "Avery", 70, 60, "neutral", "nurturing"),
            make_call("call-3", "Jordan", 80, 70, "positive", "won"),
        ]

    def list_calls_for_analytics(self):
        return self.calls


def test_dashboard_service_builds_executive_and_advisor_metrics() -> None:
    service = DashboardService(FakeAnalyticsRepository())

    executive = service.get_executive_dashboard()
    advisors = service.get_advisor_performance()
    coaching_cards = service.get_coaching_dashboard()

    assert executive.total_calls == 3
    assert executive.calls_processed_today == 3
    assert executive.average_ai_quality_score == 80
    assert executive.sentiment_distribution == {"positive": 2, "neutral": 1}
    assert advisors[0].advisor_name == "Jordan"
    assert advisors[0].average_ai_score == 85
    assert advisors[0].average_discovery_score == 83
    assert coaching_cards[0].priority_improvement == "Ask for budget range."


def test_dashboard_service_builds_coaching_card_without_category_details() -> None:
    repository = FakeAnalyticsRepository()
    repository.calls = [
        SimpleNamespace(
            id="call-legacy",
            customer_name="Legacy Customer",
            sales_rep_name="Jordan",
            status=CallStatus.COMPLETED.value,
            completed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            category_score_details=[],
            coaching_recommendations=[],
            coaching_notes=None,
        )
    ]
    service = DashboardService(repository)

    coaching_cards = service.get_coaching_dashboard()

    assert coaching_cards[0].priority_improvement == "Improve discovery consistency."
    assert (
        coaching_cards[0].practice_goal
        == "Raise Discovery by at least 5 points in the next call."
    )


def test_analytics_service_builds_chart_ready_payloads() -> None:
    service = AnalyticsService(FakeAnalyticsRepository())

    analytics = service.get_analytics_dashboard()

    assert analytics.call_volume[0].value == 3
    assert len(analytics.close_probability_trend) == 3
    assert analytics.issue_frequency[0].label == "Pricing was not quantified."
    assert analytics.top_customer_concerns[0].label == "Pricing"
    assert analytics.category_score_distribution[0].category == "discovery"
    assert analytics.advisor_leaderboard[0].advisor_name == "Jordan"
