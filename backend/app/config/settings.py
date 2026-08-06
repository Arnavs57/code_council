"""Pydantic Settings — the single source of truth for configuration.

Layout:

  * A FLAT root :class:`Settings` (env prefix ``CCAI_``) is the single source
    of truth. Flat — not nested ``BaseSettings`` models — by design: in
    pydantic-settings 2.x nested settings models read their own env file,
    letting dotenv values override real environment variables (a 12-factor
    violation) and ignoring ``_env_file=None`` (breaking test isolation).
  * Typed namespace projections (:class:`app.config.namespaces.core.CoreSettings`
    and :class:`app.config.namespaces.logging.LoggingSettings`) group the flat
    fields into the typed objects consumers use — ``settings.core.app_name``,
    ``settings.logging.level`` — without re-reading any source.
  * The model is frozen: after construction nobody can mutate global config.

Value precedence (highest first):

  1. explicit constructor arguments (tests / overrides)
  2. environment variables (``CCAI_*``)
  3. the resolved environment-file chain (see ``app/config/environment.py``)
  4. defaults below (pulled from ``app/core/constants.py``)
"""

from pathlib import Path

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config import constants as config_constants
from app.config import paths
from app.config.namespaces.core import CoreSettings
from app.config.namespaces.logging import LoggingSettings
from app.config.validators import parse_csv_list, validate_log_level, validate_port
from app.core import constants


class Settings(BaseSettings):
    """Application settings, validated once at startup. Immutable after load."""

    model_config = SettingsConfigDict(
        env_prefix="CCAI_",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        frozen=True,
    )

    # -- Schema versioning ----------------------------------------------------
    schema_version: int = config_constants.SCHEMA_VERSION

    # -- Application ----------------------------------------------------------
    app_name: str = constants.APP_NAME
    app_version: str = constants.APP_VERSION
    app_description: str = constants.APP_DESCRIPTION

    # -- Runtime --------------------------------------------------------------
    environment: str = constants.DEFAULT_ENVIRONMENT
    debug: bool | None = None  # None → derived: development environments debug
    host: str = "0.0.0.0"
    port: int = 8000

    # -- API ------------------------------------------------------------------
    api_v1_prefix: str = constants.API_V1_PREFIX
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server (frontend)
        "http://localhost:3000",  # fallback local dev origin
    ]

    # -- Logging --------------------------------------------------------------
    log_level: str = "INFO"
    log_to_file: bool = True
    log_file: Path = paths.LOG_FILE
    log_max_bytes: int = constants.LOG_MAX_BYTES
    log_backup_count: int = constants.LOG_BACKUP_COUNT

    # -- LLM provider (Ollama first, OpenAI fallback) -----------------------
    llm_provider: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:14b"
    openai_model: str = "gpt-4o-mini"
    openai_api_key: str = ""
    llm_timeout_seconds: float = 90.0
    llm_retries: int = 2

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("environment")
    @classmethod
    def _validate_environment(cls, value: str) -> str:
        env = value.strip().lower()
        if env not in constants.ENVIRONMENTS:
            raise ValueError(
                f"Unknown environment '{value}'. "
                f"Valid values: {', '.join(constants.ENVIRONMENTS)}"
            )
        return env

    @model_validator(mode="before")
    @classmethod
    def _apply_debug_default(cls, values) -> dict:
        # ``mode="before"`` so the derivation works on a frozen model: we edit
        # the input mapping instead of mutating ``self`` after construction.
        #
        # NOTE: model validators run BEFORE field validators, so ``debug`` and
        # ``environment`` here are raw values. Empty string (``CCAI_DEBUG=``
        # in a copied .env) counts as unset, and the environment is
        # normalized (strip/lower) exactly as the field validator would —
        # otherwise ``CCAI_ENVIRONMENT=DEVELOPMENT`` would yield
        # ``environment="development"`` but ``debug=False``.
        if isinstance(values, dict) and values.get("debug") in (None, ""):
            env = str(
                values.get("environment") or constants.DEFAULT_ENVIRONMENT
            ).strip().lower()
            values["debug"] = env == constants.ENVIRONMENT_DEVELOPMENT
        return values

    @field_validator("port", mode="before")
    @classmethod
    def _validate_port(cls, value: int | None) -> int:
        if value is None:
            raise ValueError("port is required (1–65535).")
        return validate_port(value)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value) -> list[str]:
        return parse_csv_list(value)

    @field_validator("log_level", mode="before")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        return validate_log_level(value)

    @field_validator("llm_provider")
    @classmethod
    def _validate_llm_provider(cls, value: str) -> str:
        provider = value.strip().lower()
        if provider not in {"ollama", "openai"}:
            raise ValueError("llm_provider must be 'ollama' or 'openai'.")
        return provider

    # -------------------------------------------------------------------------
    # Typed namespace projections
    # -------------------------------------------------------------------------
    @property
    def core(self) -> CoreSettings:
        """Typed view of the core application settings."""
        return CoreSettings(
            app_name=self.app_name,
            app_version=self.app_version,
            app_description=self.app_description,
            environment=self.environment,
            debug=bool(self.debug),
            host=self.host,
            port=self.port,
            api_v1_prefix=self.api_v1_prefix,
            cors_origins=list(self.cors_origins),
            schema_version=self.schema_version,
        )

    @property
    def logging(self) -> LoggingSettings:
        """Typed view of the logging settings."""
        return LoggingSettings(
            level=self.log_level,
            to_file=self.log_to_file,
            file=self.log_file,
            max_bytes=self.log_max_bytes,
            backup_count=self.log_backup_count,
        )
