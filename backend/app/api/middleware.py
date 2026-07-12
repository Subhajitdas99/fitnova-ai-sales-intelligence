import asyncio
import logging
import time
from uuid import uuid4

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from backend.app.core.request_context import (
    get_request_id,
    request_id_context,
)

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Attach request IDs, execution timing, and structured access logs
    to every incoming request.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())

        token = request_id_context.set(request_id)

        start_time = time.perf_counter()
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        try:
            response = await call_next(request)

            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception:
            logger.exception(
                "Unhandled request exception",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "request_id": request_id,
                },
            )
            raise

        finally:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.info(
                "HTTP request completed",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "request_id": request_id,
                },
            )

            request_id_context.reset(token)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Apply baseline HTTP security headers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)

        response.headers.setdefault(
            "X-Content-Type-Options",
            "nosniff",
        )
        response.headers.setdefault(
            "X-Frame-Options",
            "DENY",
        )
        response.headers.setdefault(
            "Referrer-Policy",
            "no-referrer",
        )
        response.headers.setdefault(
            "X-Permitted-Cross-Domain-Policies",
            "none",
        )

        return response


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """
    Abort requests that exceed the configured timeout.
    """

    def __init__(
        self,
        app,
        timeout_seconds: float,
    ) -> None:
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Reuse the request ID created by RequestContextMiddleware.
        request_id = (
            get_request_id() or request.headers.get("X-Request-ID") or str(uuid4())
        )

        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds,
            )

            response.headers.setdefault(
                "X-Request-ID",
                request_id,
            )

            return response

        except asyncio.TimeoutError:
            logger.warning(
                "HTTP request timed out",
                extra={
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": status.HTTP_504_GATEWAY_TIMEOUT,
                    "request_id": request_id,
                },
            )

            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={
                    "error": {
                        "code": "request_timeout",
                        "message": ("Request exceeded the configured timeout."),
                        "request_id": request_id,
                    }
                },
                headers={
                    "X-Request-ID": request_id,
                },
            )
