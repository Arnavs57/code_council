"""Tests for the global exception handlers (consistent JSON errors)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import register_exception_handlers


def _error_body(response) -> dict:
    body = response.json()
    assert "error" in body, f"missing error envelope: {body}"
    return body["error"]


def test_unknown_route_returns_consistent_404(client) -> None:
    response = client.get("/definitely-not-a-route")
    assert response.status_code == 404
    error = _error_body(response)
    assert error["code"] == "HTTP_404"
    assert error["message"]
    assert error["request_id"]


def test_method_not_allowed_returns_consistent_405(client) -> None:
    response = client.post("/health")
    assert response.status_code == 405
    error = _error_body(response)
    assert error["code"] == "HTTP_405"


def test_validation_error_returns_consistent_422() -> None:
    """Validation handler on a minimal app (no business routes exist yet)."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/test")
    def needs_integer(q: int) -> int:
        return q

    with TestClient(app) as test_client:
        response = test_client.get("/test", params={"q": "not-an-int"})
    assert response.status_code == 422
    error = _error_body(response)
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"], "validation details missing"


def test_unhandled_error_returns_consistent_500() -> None:
    """Unhandled exceptions become a generic 500 without leaking internals."""
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("kaboom secret detail")

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/boom")
    assert response.status_code == 500
    error = _error_body(response)
    assert error["code"] == "INTERNAL_ERROR"
    assert "kaboom" not in error["message"], "internal detail leaked"
