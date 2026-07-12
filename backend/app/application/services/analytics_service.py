from collections import Counter

from backend.app.application.dto.analytics import (
    AnalyticsDashboardResponse,
    CategoryDistributionPoint,
    FrequencyPoint,
    TimeSeriesPoint,
)
from backend.app.application.interfaces.call_repository import CallRepositoryProtocol
from backend.app.application.services.dashboard_service import DashboardService
from backend.app.domain.enums import CallStatus


class AnalyticsService:
    """Builds chart-ready analytics without coupling Streamlit to business rules."""

    def __init__(self, repository: CallRepositoryProtocol) -> None:
        self._repository = repository
        self._dashboard_service = DashboardService(repository)

    def get_analytics_dashboard(self) -> AnalyticsDashboardResponse:
        completed_calls = [
            call
            for call in self._repository.list_calls_for_analytics()
            if call.status == CallStatus.COMPLETED.value
        ]
        return AnalyticsDashboardResponse(
            call_volume=self._build_call_volume(completed_calls),
            sentiment_trend=self._build_labeled_trend(
                completed_calls,
                value_attribute="overall_sentiment",
            ),
            close_probability_trend=self._build_numeric_trend(
                completed_calls,
                value_attribute="close_probability",
            ),
            issue_frequency=self._build_frequency(
                issue
                for call in completed_calls
                for issue in (call.detected_issues or [])
            ),
            top_customer_concerns=self._build_frequency(
                concern
                for call in completed_calls
                for concern in (call.detected_objections or [])
            ),
            category_score_distribution=self._build_category_score_distribution(
                completed_calls
            ),
            advisor_leaderboard=self._dashboard_service.get_advisor_performance(),
        )

    def _build_call_volume(self, calls: list) -> list[TimeSeriesPoint]:
        counts = Counter(self._date_key(call) for call in calls)
        return [
            TimeSeriesPoint(date=date, value=float(count), label="calls")
            for date, count in sorted(counts.items())
        ]

    def _build_labeled_trend(
        self, calls: list, value_attribute: str
    ) -> list[TimeSeriesPoint]:
        points: list[TimeSeriesPoint] = []
        for call in calls:
            label = getattr(call, value_attribute, None)
            if label is None:
                continue
            points.append(
                TimeSeriesPoint(
                    date=self._date_key(call),
                    value=1.0,
                    label=str(label),
                )
            )
        return points

    def _build_numeric_trend(
        self, calls: list, value_attribute: str
    ) -> list[TimeSeriesPoint]:
        points: list[TimeSeriesPoint] = []
        for call in calls:
            value = getattr(call, value_attribute, None)
            if value is None:
                continue
            points.append(
                TimeSeriesPoint(
                    date=self._date_key(call),
                    value=float(value),
                    label=call.sales_rep_name,
                )
            )
        return points

    def _build_frequency(self, values) -> list[FrequencyPoint]:
        counts = Counter(str(value) for value in values if value)
        return [
            FrequencyPoint(label=label, value=count)
            for label, count in counts.most_common(10)
        ]

    def _build_category_score_distribution(
        self, calls: list
    ) -> list[CategoryDistributionPoint]:
        points: list[CategoryDistributionPoint] = []
        for call in calls:
            for category in call.category_score_details or []:
                points.append(
                    CategoryDistributionPoint(
                        category=str(category.get("category", "Unknown")),
                        score=float(category.get("score", 0.0)),
                        call_id=call.id,
                        advisor_name=call.sales_rep_name,
                    )
                )
        return points

    def _date_key(self, call) -> str:
        timestamp = call.completed_at or call.created_at
        return timestamp.date().isoformat()
