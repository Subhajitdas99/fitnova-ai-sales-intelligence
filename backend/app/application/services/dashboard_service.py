from backend.app.application.interfaces.call_repository import CallRepositoryProtocol


class DashboardService:
    """Builds dashboard-ready analytics aggregates."""

    def __init__(self, repository: CallRepositoryProtocol) -> None:
        self._repository = repository

    def get_overview(self) -> dict[str, object]:
        return self._repository.get_dashboard_overview()
