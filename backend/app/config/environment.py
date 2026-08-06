"""Environment detection and environment-file resolution.

Rules:

  * The active environment is read from ``CCAI_ENVIRONMENT``
    (default: ``development``).
  * Environment files are a *developer convenience, never a production
    mechanism*: they are resolved in ``development`` and ``testing`` only.
    Production config arrives exclusively through real environment variables
    (or mounted secrets) — there is no implicit fallback.
  * Inheritance: the environment-specific file (``.env.<environment>``) is
    layered ON TOP of the base ``.env``, so an environment can override a
    subset of keys while inheriting the rest. Later entries win.
  * Returning an empty tuple from :func:`resolve_env_files` means "rely on
    environment variables and defaults only" (e.g. in tests or production).
"""

import os
from pathlib import Path

from app.config import constants as config_constants
from app.config import paths
from app.core import constants


def get_current_environment() -> str:
    """Return the active environment name (validated)."""
    raw = os.getenv(config_constants.ENVIRONMENT_ENV_VAR, constants.DEFAULT_ENVIRONMENT)
    env = raw.strip().lower()
    if env not in constants.ENVIRONMENTS:
        raise ValueError(
            f"Unknown environment '{raw}' "
            f"(from {config_constants.ENVIRONMENT_ENV_VAR}). "
            f"Valid values: {', '.join(constants.ENVIRONMENTS)}."
        )
    return env


def resolve_env_files() -> tuple[Path, ...]:
    """Return existing env files to load, in ascending precedence order.

    Base ``.env`` first, then ``.env.<environment>`` (later files win on
    conflict). Env files are never loaded in production.
    """
    environment = get_current_environment()
    if environment == constants.ENVIRONMENT_PRODUCTION:
        return ()

    candidates = (
        paths.BACKEND_ROOT / config_constants.ENV_FILE_BASE,
        paths.BACKEND_ROOT / f"{config_constants.ENV_FILE_ENV_PREFIX}{environment}",
    )
    return tuple(path for path in candidates if path.is_file())
