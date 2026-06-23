"""Structured logging configuration using structlog.

All log output is JSON-formatted for machine consumption. Sensitive fields
(passwords, secrets, tokens, authorization headers) are automatically redacted
so they never leak into log stores.
"""

import logging
import re
from collections.abc import Mapping
from typing import Any

import structlog

# Keys whose values must never appear in log output.
_SENSITIVE_PATTERN = re.compile(
    r"(password|secret|token|authorization|api[_-]?key|credential)",
    re.IGNORECASE,
)

_REDACTED = "***REDACTED***"


def _filter_sensitive_data(
    _logger: Any,
    _method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Recursively redact values whose keys match a sensitive pattern."""

    def _redact(obj: Any) -> Any:
        if isinstance(obj, Mapping):
            return {
                k: _REDACTED if _SENSITIVE_PATTERN.search(str(k)) else _redact(v)
                for k, v in obj.items()
            }
        if isinstance(obj, (list, tuple)):
            return type(obj)(_redact(item) for item in obj)
        return obj

    return _redact(event_dict)  # type: ignore[return-value]


def setup_logging(log_level: str = "INFO", json_output: bool = True) -> None:
    """Configure structlog and the stdlib root logger.

    Parameters
    ----------
    log_level:
        Minimum severity (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    json_output:
        When *True* (default), render logs as JSON lines.
        When *False*, use a human-readable console renderer (useful in dev).
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _filter_sensitive_data,
    ]

    if json_output:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Quieten noisy third-party loggers
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
