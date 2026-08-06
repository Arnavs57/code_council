"""Typed namespace models.

Each module groups a slice of the application configuration into a typed,
immutable object (e.g. ``settings.logging.level``) so consumers never handle
loose strings.

Design note: namespaces are typed PROJECTIONS of the flat root ``Settings``,
not nested ``BaseSettings`` models. In pydantic-settings 2.x nested
``BaseSettings`` models read their own env file and invert the documented
precedence (dotenv overrides real env vars) and ignore ``_env_file=None``
(test isolation). The flat root remains the single source of truth; these
models provide the typed surface on top of it.
"""

from app.config.namespaces.core import CoreSettings
from app.config.namespaces.logging import LoggingSettings

__all__ = ["CoreSettings", "LoggingSettings"]
