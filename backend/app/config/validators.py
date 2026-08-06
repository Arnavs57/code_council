"""Shared field validators for the configuration layer.

Namespaces declare their fields and reference these validators; they never
reimplement parsing. Each function returns the (possibly transformed) value
for use with ``field_validator(mode="before")`` and raises ``ValueError`` on
invalid input, which Pydantic surfaces as a validation error.
"""

from app.core.helpers import split_csv

# Valid log levels accepted by the standard library logging module.
LOG_LEVELS = frozenset({"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"})

# CORS wildcard is a legitimate value; anything else must be an http(s) origin.
_ALLOWED_URL_SCHEMES = ("http://", "https://")


def validate_port(value: int | None) -> int:
    """A TCP port in the valid range 1–65535."""
    if value is None:
        raise ValueError("port is required (1–65535).")
    port = int(value)
    if not 1 <= port <= 65535:
        raise ValueError(f"Invalid port '{value}' — must be 1–65535.")
    return port


def validate_url(value: str) -> str:
    """An http(s) URL, or the CORS wildcard ``*``."""
    candidate = value.strip()
    if candidate == "*" or candidate.startswith(_ALLOWED_URL_SCHEMES):
        return candidate
    raise ValueError(f"Invalid URL '{value}' — must start with http:// or https://.")


def validate_log_level(value: str) -> str:
    """A valid standard-library logging level name."""
    level = value.upper().strip()
    if level not in LOG_LEVELS:
        raise ValueError(
            f"Invalid log level '{value}' — "
            f"valid values: {', '.join(sorted(LOG_LEVELS))}."
        )
    return level


def parse_csv_list(value: str | list[str]) -> list[str]:
    """A comma-separated string (or a list) into a cleaned list."""
    if isinstance(value, list):
        return value
    return split_csv(value)
