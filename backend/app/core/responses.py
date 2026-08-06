"""Consistent response builders for API endpoints and error handlers."""

from app.core.helpers import utc_now_iso


def infrastructure_status(
    *,
    app_name: str,
    version: str,
    environment: str,
    status: str = "ok",
) -> dict[str, str]:
    """Build the standard infrastructure response body.

    Intentionally minimal — application name, version, status, timestamp and
    environment, and nothing else (product requirement).
    """
    return {
        "app_name": app_name,
        "version": version,
        "status": status,
        "timestamp": utc_now_iso(),
        "environment": environment,
    }


def error_response(
    *,
    code: str,
    message: str,
    request_id: str | None = None,
) -> dict:
    """Build the consistent error envelope used by every exception handler."""
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
