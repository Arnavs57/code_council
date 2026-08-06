"""Configuration bootstrap — the only place configuration is assembled.

Lifecycle (see ``CONFIGURATION_ARCHITECTURE.md``)::

    resolve env files  ->  build Settings  ->  validate  ->  freeze

The environment-file chain is resolved here (never inside the model) so the
schema stays a pure declaration. Any validation error is converted into a
typed :class:`ConfigurationError` so failure paths are deterministic and the
process never boots half-configured. The model's ``frozen=True`` guarantees
immutability after construction.

The redacted audit report is emitted by ``app/config/audit.py`` once logging
is configured (see ``app/main.py``) — logging must exist before the audit
line can be formatted.
"""

from pathlib import Path

from pydantic import ValidationError

from app.config.environment import resolve_env_files
from app.config.settings import Settings
from app.core.exceptions import ConfigurationError


def build_settings(
    *, env_files: tuple[Path, ...] | None = None, **overrides
) -> Settings:
    """Load, validate and freeze the application settings.

    Args:
        env_files: explicit environment-file chain to load (used by tests);
            ``None`` resolves the chain from the active environment.
        **overrides: constructor arguments, which take precedence over
            environment variables and env files (tests / CLI tools).

    Raises:
        ConfigurationError: if any value fails validation — the process
            must never start with invalid configuration.
    """
    resolved = env_files if env_files is not None else resolve_env_files()
    try:
        return Settings(_env_file=resolved or None, **overrides)
    except ValidationError as exc:
        details = "; ".join(error["msg"] for error in exc.errors())
        raise ConfigurationError(
            f"Invalid configuration: {details or exc}"
        ) from exc
