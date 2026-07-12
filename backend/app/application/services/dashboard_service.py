from collections import Counter, defaultdict
from datetime import datetime, timezone

from backend.app.application.dto.analytics import (
    AdvisorPerformanceResponse,
    CoachingCardResponse,
    ExecutiveDashboardResponse,
)
from backend.app.application.interfaces.call_repository import CallRepositoryProtocol
from backend.app.domain.enums import CallStatus


class DashboardService:
    """Builds dashboard-ready analytics aggregates."""

    def __init__(self, repository: CallRepositoryProtocol) -> None:
        self._repository = repository

    def get_overview(self) -> dict[str, object]:
        calls = self._repository.list_calls_for_analytics()
        completed_calls = [
            call for call in calls if call.status == CallStatus.COMPLETED.value
        ]
        failed_calls = [
            call for call in calls if call.status == CallStatus.FAILED.value
        ]
        recent_calls = sorted(calls, key=lambda call: call.created_at, reverse=True)[
            :10
        ]
        return {
            "total_calls": len(calls),
            "completed_calls": len(completed_calls),
            "failed_calls": len(failed_calls),
            "processing_calls": max(
                len(calls) - len(completed_calls) - len(failed_calls), 0
            ),
            "average_close_probability": self._average(
                call.close_probability for call in completed_calls
            ),
            "average_engagement_score": self._average(
                call.engagement_score for call in completed_calls
            ),
            "sentiment_breakdown": self._distribution(
                call.overall_sentiment for call in completed_calls
            ),
            "outcome_breakdown": self._distribution(
                call.outcome for call in completed_calls
            ),
            "recent_calls": recent_calls,
        }

    def get_executive_dashboard(self) -> ExecutiveDashboardResponse:
        calls = self._repository.list_calls_for_analytics()
        completed_calls = [
            call for call in calls if call.status == CallStatus.COMPLETED.value
        ]
        today = datetime.now(timezone.utc).date()
        return ExecutiveDashboardResponse(
            average_ai_quality_score=self._average(
                call.overall_score for call in completed_calls
            ),
            average_close_probability=self._average(
                call.close_probability for call in completed_calls
            ),
            total_calls=len(calls),
            calls_processed_today=sum(
                1
                for call in completed_calls
                if call.completed_at is not None and call.completed_at.date() == today
            ),
            average_call_duration=self._average(
                call.duration_seconds for call in completed_calls
            ),
            average_engagement=self._average(
                call.engagement_score for call in completed_calls
            ),
            sentiment_distribution=self._distribution(
                call.overall_sentiment for call in completed_calls
            ),
            outcome_distribution=self._distribution(
                call.outcome for call in completed_calls
            ),
        )

    def get_advisor_performance(self) -> list[AdvisorPerformanceResponse]:
        completed_calls = [
            call
            for call in self._repository.list_calls_for_analytics()
            if call.status == CallStatus.COMPLETED.value
        ]
        grouped_calls: dict[str, list] = defaultdict(list)
        for call in completed_calls:
            grouped_calls[call.sales_rep_name].append(call)

        leaderboard = [
            AdvisorPerformanceResponse(
                advisor_name=advisor_name,
                calls_handled=len(advisor_calls),
                average_ai_score=self._average(
                    call.overall_score for call in advisor_calls
                ),
                average_close_probability=self._average(
                    call.close_probability for call in advisor_calls
                ),
                average_rapport=self._average_category(advisor_calls, "rapport"),
                average_objection_handling=self._average_category(
                    advisor_calls,
                    "objection_handling",
                ),
                average_discovery_score=self._average_category(
                    advisor_calls, "discovery"
                ),
                average_compliance_score=self._average_category(
                    advisor_calls, "compliance"
                ),
            )
            for advisor_name, advisor_calls in grouped_calls.items()
        ]
        return sorted(
            leaderboard, key=lambda advisor: advisor.average_ai_score, reverse=True
        )

    def get_coaching_dashboard(self) -> list[CoachingCardResponse]:
        completed_calls = [
            call
            for call in self._repository.list_calls_for_analytics()
            if call.status == CallStatus.COMPLETED.value
        ]
        return [self._build_coaching_card(call) for call in completed_calls]

    def _build_coaching_card(self, call) -> CoachingCardResponse:
        strengths = self._top_category_names(call, highest=True)
        weaknesses = self._top_category_names(call, highest=False)
        weakest_area = weaknesses[0] if weaknesses else "Discovery"
        priority_improvement = (
            call.coaching_recommendations[0]
            if call.coaching_recommendations
            else f"Improve {weakest_area.lower()} consistency."
        )
        return CoachingCardResponse(
            call_id=call.id,
            customer_name=call.customer_name,
            advisor_name=call.sales_rep_name,
            strengths=strengths,
            weaknesses=weaknesses,
            priority_improvement=priority_improvement,
            manager_feedback=call.coaching_notes
            or "Review the call evidence with the advisor.",
            practice_goal=f"Raise {weakest_area} by at least 5 points in the next call.",
            next_coaching_exercise=f"Role-play a {weakest_area.lower()} scenario using this call's evidence.",
        )

    def _average_category(self, calls: list, category_name: str) -> float:
        return self._average(
            self._category_score(call, category_name) for call in calls
        )

    def _category_score(self, call, category_name: str) -> float | None:
        normalized_name = category_name.lower().replace(" ", "_")
        for category in call.category_score_details or []:
            candidate = str(category.get("category", "")).lower().replace(" ", "_")
            if candidate == normalized_name:
                return float(category.get("score", 0.0))
        return None

    def _top_category_names(self, call, highest: bool) -> list[str]:
        category_details = [
            (
                str(category.get("category", "Unknown")).replace("_", " ").title(),
                float(category.get("score", 0.0)),
            )
            for category in call.category_score_details or []
        ]
        if not category_details:
            return []
        category_details.sort(key=lambda item: item[1], reverse=highest)
        return [name for name, _ in category_details[:2]]

    def _average(self, values) -> float:
        numeric_values = [float(value) for value in values if value is not None]
        if not numeric_values:
            return 0.0
        return round(sum(numeric_values) / len(numeric_values), 2)

    def _distribution(self, values) -> dict[str, int]:
        return dict(Counter(str(value) for value in values if value is not None))
