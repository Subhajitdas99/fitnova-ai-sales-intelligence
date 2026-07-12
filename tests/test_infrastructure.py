import asyncio

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import DatabaseError

from backend.app.api.exception_handlers import register_exception_handlers
from backend.app.api.middleware import (
    RequestContextMiddleware,
    RequestTimeoutMiddleware,
    SecurityHeadersMiddleware,
)
from backend.app.core.config import Settings
from backend.app.core.exceptions import (
    ApplicationError,
    ExternalServiceError,
    ResourceNotFoundError,
    ServiceConfigurationError,
    StartupConfigurationError,
)
from backend.app.core.request_context import get_request_id
from backend.main import app as main_app

# ------------------------------------------------------------------------------
# 1. Configuration & Startup Validation Tests
# ------------------------------------------------------------------------------


def test_settings_default_values() -> None:
    """Verify default config settings are correctly instantiated."""
    settings = Settings()
    assert settings.app_name == "FitNova AI Sales Intelligence"
    assert settings.app_version == "1.0.0"
    assert settings.environment == "development"
    assert settings.debug is False
    assert settings.log_level == "INFO"


def test_settings_aliases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify alias variables are read correctly."""
    monkeypatch.setenv("HUGGINGFACE_TOKEN", "hf-token-123")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")

    settings = Settings()
    assert settings.huggingface_auth_token == "hf-token-123"
    assert settings.database_url == "sqlite:///test.db"


def test_settings_blank_strings_to_none() -> None:
    """Verify blank or empty string configs are parsed as None."""
    settings = Settings(
        openai_api_key="   ",
        openrouter_api_key="",
        huggingface_auth_token=" \t\n ",
    )
    assert settings.openai_api_key is None
    assert settings.openrouter_api_key is None
    assert settings.huggingface_auth_token is None


def test_settings_validation_for_startup_dev() -> None:
    """Verify startup validation does not crash in development/local environment."""
    settings = Settings(
        environment="development",
        analysis_provider="openrouter",
        openrouter_api_key=None,
    )
    # Should not raise any exceptions
    settings.validate_for_startup()


def test_settings_validation_for_startup_prod_missing_keys() -> None:
    """Verify startup validation raises StartupConfigurationError in production with missing keys."""
    settings = Settings(
        environment="production",
        analysis_provider="openrouter",
        openrouter_api_key=None,
    )
    with pytest.raises(StartupConfigurationError) as exc_info:
        settings.validate_for_startup()
    assert "Missing required production configuration" in str(exc_info.value)
    assert "OPENROUTER_API_KEY" in str(exc_info.value)


def test_settings_validation_for_startup_prod_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify startup validation passes in production when correctly configured."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "valid-key")
    settings = Settings(
        environment="production",
        analysis_provider="openrouter",
    )
    # Should pass without raising
    settings.validate_for_startup()


# ------------------------------------------------------------------------------
# 2. Health Endpoints Tests
# ------------------------------------------------------------------------------


def test_liveness_endpoint() -> None:
    """Verify that the liveness probe returns healthy status code and metadata."""
    with TestClient(main_app) as client:
        response = client.get("/health/live")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_readiness_endpoint() -> None:
    """Verify that the readiness probe successfully queries component status."""
    with TestClient(main_app) as client:
        response = client.get("/health/ready")

    # Ready status depends on whether local test DB and storage are accessible,
    # which they should be in the test environment context.
    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_503_SERVICE_UNAVAILABLE,
    )
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "storage" in data["checks"]
    assert "openrouter" in data["checks"]


# ------------------------------------------------------------------------------
# 3. Middleware Tests (using isolated FastAPI app)
# ------------------------------------------------------------------------------


@pytest.fixture
def middleware_test_app() -> FastAPI:
    """Create a clean FastAPI application to test middleware behavior."""
    app = FastAPI()

    app.add_middleware(RequestTimeoutMiddleware, timeout_seconds=0.1)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)

    @app.get("/ok")
    async def ok_route() -> dict[str, str | None]:
        return {"request_id": get_request_id()}

    @app.get("/slow")
    async def slow_route() -> dict[str, str]:
        await asyncio.sleep(0.5)
        return {"status": "too-slow"}

    return app


def test_request_context_middleware(middleware_test_app: FastAPI) -> None:
    """Verify request context middleware generates and binds Request IDs."""
    client = TestClient(middleware_test_app)

    # 1. Custom request ID passed via headers
    custom_id = "test-req-id-12345"
    response = client.get("/ok", headers={"X-Request-ID": custom_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("X-Request-ID") == custom_id
    assert response.json()["request_id"] == custom_id

    # 2. No request ID passed - should generate a new UUID
    response_auto = client.get("/ok")
    assert response_auto.status_code == status.HTTP_200_OK
    generated_id = response_auto.headers.get("X-Request-ID")
    assert generated_id is not None
    assert len(generated_id) > 10
    assert response_auto.json()["request_id"] == generated_id


def test_security_headers_middleware(middleware_test_app: FastAPI) -> None:
    """Verify security headers middleware applies secure browser options."""
    client = TestClient(middleware_test_app)
    response = client.get("/ok")

    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert response.headers.get("X-Permitted-Cross-Domain-Policies") == "none"


def test_request_timeout_middleware(middleware_test_app: FastAPI) -> None:
    """Verify request timeout middleware cuts off slow endpoints and returns 504."""
    client = TestClient(middleware_test_app)
    response = client.get("/slow")

    assert response.status_code == status.HTTP_504_GATEWAY_TIMEOUT
    data = response.json()
    assert data["error"]["code"] == "request_timeout"
    assert "Request exceeded the configured timeout." in data["error"]["message"]


# ------------------------------------------------------------------------------
# 4. Exception Handler Tests (using isolated FastAPI app)
# ------------------------------------------------------------------------------


@pytest.fixture
def exception_test_app() -> FastAPI:
    """Create a FastAPI application with registered exception handlers for routing tests."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    def raise_not_found() -> None:
        raise ResourceNotFoundError("Call record 101 not found.")

    @app.get("/external-error")
    def raise_external() -> None:
        raise ExternalServiceError("OpenRouter request failed.")

    @app.get("/database-error")
    def raise_db() -> None:
        raise DatabaseError("SELECT *", {}, Exception("Database locked"))

    @app.get("/service-config-error")
    def raise_service_config() -> None:
        raise ServiceConfigurationError("Provider not configured.")

    @app.get("/app-error")
    def raise_app() -> None:
        raise ApplicationError("Invalid workflow state.")

    @app.get("/http-error")
    def raise_http() -> None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied."
        )

    @app.get("/unexpected-error")
    def raise_unexpected() -> None:
        raise ValueError("General Python error.")

    return app


def test_exception_handler_resource_not_found(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/not-found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["error"]["code"] == "not_found"
    assert "Call record 101 not found." in response.json()["error"]["message"]


def test_exception_handler_external_service(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/external-error")
    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.json()["error"]["code"] == "external_service_error"
    assert "OpenRouter request failed." in response.json()["error"]["message"]


def test_exception_handler_database_error(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/database-error")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["error"]["code"] == "database_error"
    assert "Database operation failed." in response.json()["error"]["message"]


def test_exception_handler_service_configuration(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/service-config-error")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["error"]["code"] == "service_configuration_error"
    assert "Provider not configured." in response.json()["error"]["message"]


def test_exception_handler_application_error(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/app-error")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error"]["code"] == "application_error"
    assert "Invalid workflow state." in response.json()["error"]["message"]


def test_exception_handler_http_exception(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/http-error")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["error"]["code"] == "http_error"
    assert "Access denied." in response.json()["error"]["message"]


def test_exception_handler_unexpected_error(exception_test_app: FastAPI) -> None:
    client = TestClient(exception_test_app, raise_server_exceptions=False)
    response = client.get("/unexpected-error")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json()["error"]["code"] == "internal_server_error"
    assert "Unexpected application error." in response.json()["error"]["message"]
