"""
Minimal structured (JSON) logging.

Why JSON logs? In production (CloudWatch, Datadog, Sentry breadcrumbs, etc.) machine-
parseable logs let you search by field — e.g. all lines where event="observation_added"
and patient_id=X. That's the "instrument what you build" habit the job asks for.
"""
import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Any extra={...} fields passed to the logger get merged in.
        if hasattr(record, "context") and isinstance(record.context, dict):
            payload.update(record.context)
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def log_event(logger: logging.Logger, event: str, **fields) -> None:
    """Helper: log a structured event. Usage: log_event(log, 'patient_created', id=p.id)"""
    logger.info(event, extra={"context": {"event": event, **fields}})
