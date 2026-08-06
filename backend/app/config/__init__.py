"""Configuration management: settings schema, environment detection, loader.

Public surface — every module in the platform imports ``settings`` from
``app.config`` (or ``app.config.config``). Internal modules (``bootstrap``,
``audit``, ``validators``, ``paths``, ``namespaces``) are importable but not
part of the contract.
"""

from app.config.audit import build_audit_report, log_config_audit
from app.config.bootstrap import build_settings
from app.config.config import get_settings, settings
from app.config.environment import get_current_environment, resolve_env_files
from app.config.settings import Settings

__all__ = [
    "Settings",
    "build_settings",
    "get_settings",
    "settings",
    "get_current_environment",
    "resolve_env_files",
    "build_audit_report",
    "log_config_audit",
]
