"""Application-wide constants.

Magic numbers and hard-coded strings shared across the codebase live here so
they are defined exactly once. Nothing in this module may import from other
application packages: it sits at the bottom of the dependency graph.
"""

# ---------------------------------------------------------------------------
# Application identity
# ---------------------------------------------------------------------------
APP_NAME: str = "Code Council AI"
APP_VERSION: str = "0.1.0"
APP_DESCRIPTION: str = (
    "AI Engineering Governance Platform. Multiple specialized AI agents "
    "collaboratively review software repositories and reach a collective "
    "release decision."
)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
# NOTE: the env var *name* (CCAI_ENVIRONMENT) is config vocabulary and lives
# in app/config/constants.py. The environment *values* below are static
# defaults and belong here.
ENVIRONMENT_DEVELOPMENT: str = "development"
ENVIRONMENT_TESTING: str = "testing"
ENVIRONMENT_PRODUCTION: str = "production"
ENVIRONMENTS: tuple[str, ...] = (
    ENVIRONMENT_DEVELOPMENT,
    ENVIRONMENT_TESTING,
    ENVIRONMENT_PRODUCTION,
)
DEFAULT_ENVIRONMENT: str = ENVIRONMENT_DEVELOPMENT

# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------
API_V1_PREFIX: str = "/api/v1"

# ---------------------------------------------------------------------------
# Default limits (consumed by future pagination / rate-limiting features)
# ---------------------------------------------------------------------------
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100

# ---------------------------------------------------------------------------
# Headers
# ---------------------------------------------------------------------------
HEADER_REQUEST_ID: str = "X-Request-ID"

# ---------------------------------------------------------------------------
# Logging limits
# ---------------------------------------------------------------------------
# NOTE: LOG_DIR / LOG_FILE now live in app/config/paths.py (root-anchored).
LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10 MiB per log file before rotation
LOG_BACKUP_COUNT: int = 5
