import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError

from backend.app.core.exceptions import (
    ApplicationError,
    ExternalServiceError,
    ResourceNotFoundError,
    ServiceConfigurationError,
)
from backend.app.core.request_context import get_request_id

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(ValidationError, handle_validation_error)
    app.add_exception_handler(ExternalServiceError, handle_external_service_error)
    app.add_exception_handler(DatabaseError, handle_database_error)
    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(ResourceNotFoundError, handle_not_found_error)
    app.add_exception_handler(ServiceConfigurationError, handle_configuration_error)
    app.add_exception_handler(ApplicationError, handle_application_error)
    app.add_exception_handler(Exception, handle_unexpected_error)


async def handle_request_validation_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    logger.warning(
        "Request validation failed",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="Request validation failed.",
        details=jsonable_encoder(exc.errors()),
    )


async def handle_validation_error(
    request: Request, exc: ValidationError
) -> JSONResponse:
    logger.warning(
        "Response validation failed",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )
    return _error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="Validation failed.",
        details=jsonable_encoder(exc.errors()),
    )


async def handle_external_service_error(
    request: Request, exc: ExternalServiceError
) -> JSONResponse:
    logger.exception(
        "External service error",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_502_BAD_GATEWAY,
        code="external_service_error",
        message=str(exc),
    )


async def handle_database_error(request: Request, exc: DatabaseError) -> JSONResponse:
    logger.exception(
        "Database error",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="database_error",
        message="Database operation failed.",
    )


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP exception",
        extra={
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )
    return _error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
        headers=exc.headers,
    )


async def handle_not_found_error(
    request: Request, exc: ResourceNotFoundError
) -> JSONResponse:
    logger.warning(
        "Resource not found",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="not_found",
        message=str(exc),
    )


async def handle_configuration_error(
    request: Request,
    exc: ServiceConfigurationError,
) -> JSONResponse:
    logger.exception(
        "Service configuration error",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="service_configuration_error",
        message=str(exc),
    )


async def handle_application_error(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    logger.exception(
        "Application error",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="application_error",
        message=str(exc),
    )


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unexpected application error",
        extra={"endpoint": request.url.path, "method": request.method},
    )
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        message="Unexpected application error.",
    )


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: object | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request_id = get_request_id()
    content: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        content["error"]["details"] = details  # type: ignore[index]

    response_headers = dict(headers or {})
    if request_id:
        response_headers["X-Request-ID"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=response_headers,
    )
