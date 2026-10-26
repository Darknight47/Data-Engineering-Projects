
import json
import logging
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """Format log records as structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include optional structured fields when supplied by the caller.
        for field in (
            "event",
            "stage",
            "attempt",
            "max_attempts",
            "status_code",
            "delay_seconds",
            "file_path",
            "catalog",
            "schema",
            "table_name",
            "invalid_count",
        ):
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        if record.exc_info:
            log_entry["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(log_entry, default=str)


def configure_logging() -> None:
    """Configure application-wide JSON logging to standard output."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
