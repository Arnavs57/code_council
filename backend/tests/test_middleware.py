"""Tests for the middleware stack."""

import logging


def test_response_carries_request_id(client) -> None:
    response = client.get("/health")
    assert response.headers.get("X-Request-ID"), "X-Request-ID header missing"


def test_incoming_request_id_is_propagated(client) -> None:
    response = client.get("/health", headers={"X-Request-ID": "trace-123"})
    assert response.headers.get("X-Request-ID") == "trace-123"


def test_cors_preflight_allows_configured_origin(client) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == \
        "http://localhost:5173"


def test_cors_exposes_request_id_header(client) -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    exposed = response.headers.get("access-control-expose-headers", "")
    assert "X-Request-ID" in exposed


def test_access_log_includes_request_id(client) -> None:
    """Proves the RequestID middleware runs OUTSIDE the access-log
    middleware (the id is already set when the access log fires)."""
    records: list[logging.LogRecord] = []
    handler = logging.Handler()
    handler.emit = records.append  # type: ignore[method-assign]
    access_logger = logging.getLogger("app.access")
    access_logger.addHandler(handler)
    try:
        client.get("/health")
    finally:
        access_logger.removeHandler(handler)

    access_records = [r for r in records if r.getMessage() == "http_request"]
    assert access_records, "no access-log line produced"
    assert access_records[0].request_id, "request_id missing from access log"
