from typing import Any

import requests


class FitNovaApiClient:
    """Thin HTTP client for the FastAPI backend."""

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    def get_dashboard_overview(self) -> dict[str, Any]:
        response = requests.get(
            f"{self._base_url}/api/v1/dashboard/overview", timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_executive_dashboard(self) -> dict[str, Any]:
        response = requests.get(
            f"{self._base_url}/api/v1/dashboard/executive", timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_advisor_performance(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self._base_url}/api/v1/dashboard/advisors", timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_coaching_dashboard(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self._base_url}/api/v1/dashboard/coaching", timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_analytics_dashboard(self) -> dict[str, Any]:
        response = requests.get(f"{self._base_url}/api/v1/analytics", timeout=30)
        response.raise_for_status()
        return response.json()

    def list_calls(self, limit: int = 50) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self._base_url}/api/v1/calls",
            params={"limit": limit},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_call(self, call_id: str) -> dict[str, Any]:
        response = requests.get(f"{self._base_url}/api/v1/calls/{call_id}", timeout=30)
        response.raise_for_status()
        return response.json()

    def upload_call(
        self,
        file_name: str,
        file_bytes: bytes,
        customer_name: str,
        sales_rep_name: str,
        language: str,
        notes: str,
    ) -> dict[str, Any]:
        response = requests.post(
            f"{self._base_url}/api/v1/calls/upload",
            files={"file": (file_name, file_bytes)},
            data={
                "customer_name": customer_name,
                "sales_rep_name": sales_rep_name,
                "language": language,
                "notes": notes,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()
