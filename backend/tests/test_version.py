"""Tests for the GET /version endpoint."""

from app.core.constants import APP_VERSION


def test_version_matches_constants(client) -> None:
    response = client.get("/version")
    assert response.status_code == 200
    assert response.json()["version"] == APP_VERSION


def test_version_under_api_prefix(client) -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json()["version"] == APP_VERSION
