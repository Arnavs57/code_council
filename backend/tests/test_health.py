"""Tests for the GET /health endpoint."""

from app.core.constants import ENVIRONMENTS


def test_health_returns_ok(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["environment"] in ENVIRONMENTS


def test_health_under_api_prefix(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
