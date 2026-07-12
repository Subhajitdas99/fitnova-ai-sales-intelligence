# FitNova AI Sales Intelligence - Logging Guide

This document describes how structured and request-aware logging is implemented and managed within FitNova.

## 1. Overview of Logging Architecture

FitNova uses structured, JSON-ready logs in production to integrate cleanly with log management platforms (such as Elasticsearch/Kibana, Datadog, or GCP Cloud Logging).

Logging is configured during application startup via `configure_logging()` in [logging.py](file:///f:/fitnova-ai/backend/app/core/logging.py).

## 2. Request Correlation & Context

Every incoming HTTP request goes through the [RequestContextMiddleware](file:///f:/fitnova-ai/backend/app/api/middleware.py) which handles tracing context:

1. **Request ID Generation**:
   - If the client sends an `X-Request-ID` header, the middleware preserves it.
   - Otherwise, a new UUID is generated as the unique Request ID.
2. **Context Binding**:
   - The Request ID is set in a context-local variable (`request_id_context`), which is accessible globally in the thread or async task execution context.
3. **Response Propagation**:
   - The Request ID is attached to the response headers under `X-Request-ID`.
4. **Context Logging**:
   - The logging filter injects the active Request ID (if present) into every log record.

### Example log payload format:

```json
{
  "timestamp": "2026-07-12T14:19:58Z",
  "level": "INFO",
  "name": "backend.app.api.middleware",
  "message": "HTTP request completed",
  "request_id": "b34db997-f52a-4bb2-8be0-adf2331e9f36",
  "endpoint": "/api/v1/dashboard/overview",
  "method": "GET",
  "status_code": 200,
  "duration_ms": 12.4
}
```

## 3. Log Levels & Behavior

- **DEBUG**: Verbose details for troubleshooting.
- **INFO**: Standard operational flows (e.g. startup, request completion, service execution status).
- **WARNING**: Non-critical anomalies (e.g. client validation failures, minor retries).
- **ERROR**: Critical task errors (e.g. failed transcription task, database connection errors).
- **CRITICAL**: Hard failures preventing the system from running.

Configure the log level using `FITNOVA_LOG_LEVEL` environment variable.

## 4. Unhandled Exception Logging

All unhandled exceptions thrown by routing paths or application services are caught by:
1. `RequestContextMiddleware` to ensure the exception details and traceback are logged under `logger.exception`.
2. Custom FastAPI exception handlers (configured in [exception_handlers.py](file:///f:/fitnova-ai/backend/app/api/exception_handlers.py)) to return a standardized JSON error response including the `request_id` to the client. This allows developers to correlate client errors back to server logs.
