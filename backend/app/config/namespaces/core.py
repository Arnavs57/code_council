"""Core application settings — typed projection of the root ``Settings``.

Env-var contract (flat, prefix ``CCAI_``)::

    CCAI_APP_NAME         application display name
    CCAI_APP_VERSION      application version
    CCAI_APP_DESCRIPTION  one-line description
    CCAI_ENVIRONMENT      development | testing | production
    CCAI_DEBUG            true/false (empty → derived from environment)
    CCAI_HOST             bind address
    CCAI_PORT             bind port
    CCAI_API_V1_PREFIX    versioned API prefix
    CCAI_CORS_ORIGINS     comma-separated allowed origins
"""

from pydantic import BaseModel, ConfigDict

from app.core import constants


class CoreSettings(BaseModel):
    """Application identity, runtime and API surface settings."""

    model_config = ConfigDict(frozen=True)

    app_name: str
    app_version: str
    app_description: str
    environment: str
    debug: bool
    host: str
    port: int
    api_v1_prefix: str
    cors_origins: list[str]
    schema_version: int

    # -- Convenience predicates ----------------------------------------------
    @property
    def is_production(self) -> bool:
        """True when running in the production environment."""
        return self.environment == constants.ENVIRONMENT_PRODUCTION

    @property
    def is_development(self) -> bool:
        """True when running in the development environment."""
        return self.environment == constants.ENVIRONMENT_DEVELOPMENT

    @property
    def docs_enabled(self) -> bool:
        """Interactive docs (OpenAPI UI) are exposed outside production."""
        return not self.is_production
