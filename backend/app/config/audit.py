"""Redacted configuration audit.

Produces a startup report of what the process is actually running with:
which fields were explicitly set (env / file / args) versus defaulted, with
any secret-looking values masked. Secret *names* may be logged; secret
*values* never are.
"""

import logging
from typing import Any

from app.config.settings import Settings

logger = logging.getLogger("app.config")

# Field names that hint at secret material — their values are always masked.
# Substring match, but "api" is deliberately excluded: names like api_v1_prefix
# are not secrets, and a too-broad hint would mask harmless configuration.
_SECRET_HINTS = ("key", "token", "secret", "password", "credential")


def _is_secret_field(name: str) -> bool:
    return any(hint in name.lower() for hint in _SECRET_HINTS)


def _redact(name: str, value: Any) -> Any:
    """Mask secret values while leaving everything else intact."""
    if _is_secret_field(name) and value not in (None, "", False):
        return "***"
    return value


def build_audit_report(settings: Settings) -> dict[str, Any]:
    """Build a redacted snapshot of the effective configuration.

    ``explicitly_set`` lists the fields that came from a source other than
    their default (env var, env file or constructor argument) — answering
    "what is this pod actually running with?" from a single log line.
    """
    raw = settings.model_dump()
    return {
        "schema_version": settings.schema_version,
        "environment": settings.environment,
        "explicitly_set": sorted(settings.model_fields_set),
        "values": {name: _redact(name, value) for name, value in raw.items()},
    }


def log_config_audit(settings: Settings) -> None:
    """Emit the redacted configuration report as one structured log line."""
    logger.info("config_audit", extra={"config": build_audit_report(settings)})
