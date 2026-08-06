"""Typed exception hierarchy for the application.

Handlers in ``app/api/errors.py`` map these exceptions to consistent HTTP
responses. Adding a new error type should never require changing callers.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    code: str = "APP_ERROR"
    status_code: int = 500

    def __init__(
        self,
        message: str = "An application error occurred.",
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code

    def __str__(self) -> str:
        return self.message


class ConfigurationError(AppError):
    """Raised when the application is misconfigured (fail-fast at startup)."""

    code = "CONFIGURATION_ERROR"
    status_code = 500


class ResourceNotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    code = "RESOURCE_NOT_FOUND"
    status_code = 404


class ServiceUnavailableError(AppError):
    """Raised when a downstream dependency (DB, bus, LLM) is unavailable."""

    code = "SERVICE_UNAVAILABLE"
    status_code = 503
