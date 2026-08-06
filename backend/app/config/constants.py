"""Configuration-domain vocabulary.

Boundary rule (see ``CONFIGURATION_ARCHITECTURE.md`` §12):

  * This module owns KEY NAMES and FILE NAMES — the vocabulary of the
    configuration layer (prefixes, env var names, env file names, sentinels).
  * ``app/core/constants.py`` owns STATIC DEFAULT VALUES (app identity,
    environment enum, limits) and never defines config key names.

Nothing here may import from other application packages.
"""

# ---------------------------------------------------------------------------
# Root prefix and per-module sub-prefixes
# ---------------------------------------------------------------------------
CONFIG_PREFIX: str = "CCAI"

PREFIX_LOGGING: str = "CCAI_LOG_"
PREFIX_DATABASE: str = "CCAI_DB_"       # reserved — Phase 2
PREFIX_BUS: str = "CCAI_BUS_"           # reserved — Phase 3
PREFIX_LLM: str = "CCAI_LLM_"           # reserved — Phase 3
PREFIX_GOVERNANCE: str = "CCAI_GOV_"    # reserved — Phase 3
PREFIX_TOOLS: str = "CCAI_TOOLS_"       # reserved — Phase 3
PREFIX_PLUGIN: str = "CCAI_PLUGIN_"     # any future plugin

# ---------------------------------------------------------------------------
# Env var names
# ---------------------------------------------------------------------------
ENVIRONMENT_ENV_VAR: str = "CCAI_ENVIRONMENT"

# ---------------------------------------------------------------------------
# Env file names (developer convenience — never loaded in production)
# ---------------------------------------------------------------------------
ENV_FILE_BASE: str = ".env"
ENV_FILE_ENV_PREFIX: str = ".env."
ENV_FILE_ENCODING: str = "utf-8"

# ---------------------------------------------------------------------------
# Sentinels
# ---------------------------------------------------------------------------
# Placeholder value in committed .env templates; the bootstrap layer refuses
# to start with a sentinel in place of a required secret.
CHANGE_ME_SENTINEL: str = "CHANGE_ME"

# ---------------------------------------------------------------------------
# Schema versioning
# ---------------------------------------------------------------------------
SCHEMA_VERSION: int = 1
