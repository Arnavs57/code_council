"""Tests for configuration management (settings, namespaces, bootstrap)."""

import pydantic
import pytest

from app.config.audit import build_audit_report
from app.config.bootstrap import build_settings
from app.config.config import get_settings
from app.config.environment import get_current_environment, resolve_env_files
from app.config.settings import Settings
from app.core import constants


def test_default_environment_is_valid() -> None:
    assert get_current_environment() in constants.ENVIRONMENTS


def test_settings_load_defaults_without_env_file() -> None:
    settings = Settings(_env_file=None)
    assert settings.app_name == constants.APP_NAME
    assert settings.environment in constants.ENVIRONMENTS
    assert settings.api_v1_prefix == constants.API_V1_PREFIX


def test_environment_override_via_env_var(monkeypatch) -> None:
    monkeypatch.setenv("CCAI_ENVIRONMENT", "testing")
    get_settings.cache_clear()
    try:
        settings = get_settings()
        assert settings.environment == constants.ENVIRONMENT_TESTING
        assert settings.core.environment == constants.ENVIRONMENT_TESTING
    finally:
        get_settings.cache_clear()


def test_invalid_environment_rejected(monkeypatch) -> None:
    monkeypatch.setenv("CCAI_ENVIRONMENT", "mars")
    with pytest.raises(ValueError):
        get_current_environment()
    with pytest.raises(pydantic.ValidationError):
        Settings(_env_file=None, environment="mars")


def test_debug_derived_in_development() -> None:
    settings = Settings(_env_file=None, environment="development")
    assert settings.debug is True
    assert settings.core.debug is True


def test_debug_derived_false_in_production() -> None:
    settings = Settings(_env_file=None, environment="production")
    assert settings.debug is False
    assert settings.core.debug is False


def test_debug_explicit_override_wins() -> None:
    settings = Settings(_env_file=None, environment="production", debug=True)
    assert settings.debug is True


def test_debug_empty_env_var_derives_from_environment() -> None:
    # ``CCAI_DEBUG=`` (empty, as shipped in a copied .env) must count as unset
    # and fall back to environment derivation — not stay ``None``.
    settings = Settings(_env_file=None, environment="development", debug="")
    assert settings.debug is True
    settings = Settings(_env_file=None, environment="production", debug="")
    assert settings.debug is False


def test_debug_derivation_is_case_insensitive() -> None:
    # ``_validate_environment`` lowercases after the derivation runs, so the
    # derivation itself must normalize — otherwise a valid-but-uppercase
    # environment would yield debug=False with environment="development".
    settings = Settings(_env_file=None, environment="DEVELOPMENT")
    assert settings.environment == "development"
    assert settings.debug is True


def test_cors_origins_parsed_from_csv() -> None:
    settings = Settings(
        _env_file=None, cors_origins="https://a.example, https://b.example"
    )
    assert settings.core.cors_origins == ["https://a.example", "https://b.example"]


def test_invalid_log_level_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        Settings(_env_file=None, log_level="SHOUTY")


def test_invalid_port_rejected() -> None:
    with pytest.raises(pydantic.ValidationError):
        Settings(_env_file=None, port=99999)


# ---------------------------------------------------------------------------
# Namespace projections
# ---------------------------------------------------------------------------


def test_core_namespace_is_typed_view() -> None:
    settings = Settings(_env_file=None)
    assert settings.core.app_name == settings.app_name
    assert settings.core.schema_version == settings.schema_version
    assert settings.core.is_production is (
        settings.environment == constants.ENVIRONMENT_PRODUCTION
    )
    assert settings.core.docs_enabled is not settings.core.is_production


def test_logging_namespace_is_typed_view() -> None:
    settings = Settings(_env_file=None)
    assert settings.logging.level == settings.log_level
    assert settings.logging.to_file == settings.log_to_file
    assert settings.logging.file == settings.log_file


def test_namespace_is_immutable() -> None:
    settings = Settings(_env_file=None)
    with pytest.raises(pydantic.ValidationError):
        settings.core.app_name = "hacked"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Frozen singleton
# ---------------------------------------------------------------------------


def test_settings_are_frozen() -> None:
    settings = Settings(_env_file=None)
    with pytest.raises(pydantic.ValidationError):
        settings.app_name = "hacked"  # type: ignore[misc]


def test_singleton_is_cached() -> None:
    get_settings.cache_clear()
    try:
        first = get_settings()
        second = get_settings()
        assert first is second
    finally:
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Environment inheritance (layered env files)
# ---------------------------------------------------------------------------


def test_resolve_env_files_returns_a_tuple(monkeypatch) -> None:
    # The real chain resolves against the backend root; it must always be a
    # tuple of existing files and never crash, whatever the working tree has.
    monkeypatch.setenv("CCAI_ENVIRONMENT", "testing")
    result = resolve_env_files()
    assert isinstance(result, tuple)
    assert all(path.is_file() for path in result)


def test_environment_layer_wins_over_base(monkeypatch, tmp_path) -> None:
    (tmp_path / ".env").write_text("CCAI_APP_NAME=BaseApp\n", encoding="utf-8")
    (tmp_path / ".env.testing").write_text(
        "CCAI_APP_NAME=TestingApp\n", encoding="utf-8"
    )
    settings = build_settings(
        env_files=(
            tmp_path / ".env",
            tmp_path / ".env.testing",
        ),
        environment="testing",
    )
    assert settings.app_name == "TestingApp"  # environment layer wins


def test_layered_inheritance_keeps_base_values(monkeypatch, tmp_path) -> None:
    (tmp_path / ".env").write_text(
        "CCAI_APP_NAME=BaseApp\nCCAI_LOG_LEVEL=INFO\n", encoding="utf-8"
    )
    (tmp_path / ".env.testing").write_text(
        "CCAI_LOG_LEVEL=DEBUG\n", encoding="utf-8"
    )
    settings = build_settings(
        env_files=(
            tmp_path / ".env",
            tmp_path / ".env.testing",
        ),
        environment="testing",
    )
    # base key survives, environment layer overrides
    assert settings.app_name == "BaseApp"
    assert settings.log_level == "DEBUG"


def test_env_vars_beat_env_files(monkeypatch, tmp_path) -> None:
    (tmp_path / ".env").write_text("CCAI_APP_NAME=FromFile\n", encoding="utf-8")
    monkeypatch.setenv("CCAI_APP_NAME", "FromEnv")
    try:
        settings = build_settings(env_files=(tmp_path / ".env",))
        assert settings.app_name == "FromEnv"  # 12-factor: env wins
    finally:
        monkeypatch.delenv("CCAI_APP_NAME")


def test_production_never_loads_env_files(monkeypatch) -> None:
    monkeypatch.setenv("CCAI_ENVIRONMENT", "production")
    assert resolve_env_files() == ()


def test_bootstrap_fail_fast_on_invalid_config() -> None:
    from app.core.exceptions import ConfigurationError

    with pytest.raises(ConfigurationError):
        build_settings(environment="mars")


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


def test_audit_report_shape() -> None:
    settings = Settings(_env_file=None, app_name="X")
    report = build_audit_report(settings)
    assert report["environment"] == settings.environment
    assert report["schema_version"] == settings.schema_version
    assert report["values"]["app_name"] == "X"
    assert "values" in report and isinstance(report["values"], dict)


def test_audit_redaction_masks_secret_style_keys() -> None:
    from app.config.audit import _redact

    assert _redact("api_key", "super-secret") == "***"
    assert _redact("db_password", "hunter2") == "***"
    assert _redact("cors_origins", "http://localhost") == "http://localhost"
    assert _redact("api_key", "") == ""  # empty values are not masked


def test_audit_report_lists_explicitly_set_fields() -> None:
    settings = Settings(_env_file=None, app_name="Explicit")
    report = build_audit_report(settings)
    assert "app_name" in report["explicitly_set"]
    assert "app_version" not in report["explicitly_set"]
