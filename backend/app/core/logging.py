import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.app.core.request_context import get_request_id

# Standard LogRecord attributes that should not be duplicated
_RESERVED_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JsonLogFormatter(logging.Formatter):
    """
    Format application logs as structured JSON.

    Each log entry includes:
    - UTC timestamp
    - log level
    - logger name
    - message
    - request ID (if available)
    - any custom extra fields
    - formatted exception (if present)
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None) or get_request_id(),
        }

        # Include any custom "extra" fields
        for key, value in record.__dict__.items():
            if key not in _RESERVED_LOG_RECORD_FIELDS and key not in payload:
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            default=str,
            separators=(",", ":"),
        )


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure application-wide JSON logging.

    Safe to call multiple times (e.g. during FastAPI reload).
    """

    root_logger = logging.getLogger()

    # Avoid duplicate handlers on reload
    root_logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root_logger.addHandler(handler)

    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Child loggers propagate to the configured root logger
    root_logger.propagate = False


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a configured logger.

    This wrapper ensures all modules obtain loggers from the
    same logging hierarchy.
    """
    return logging.getLogger(name)
