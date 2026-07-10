from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_dashboard_overview_endpoint_returns_payload() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/dashboard/overview")

    payload = response.json()
    assert response.status_code == 200
    assert "total_calls" in payload
    assert "recent_calls" in payload
