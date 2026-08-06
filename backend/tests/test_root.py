"""Tests for the GET / endpoint."""

from app.core.constants import APP_NAME, ENVIRONMENTS


def test_root_returns_application_info(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {
        "app_name",
        "version",
        "status",
        "timestamp",
        "environment",
    }
    assert body["app_name"] == APP_NAME
    assert body["environment"] in ENVIRONMENTS
    assert body["status"] == "ok"
    assert body["version"]
    assert body["timestamp"]


def test_root_is_also_available_under_api_prefix(client) -> None:
    response = client.get("/api/v1/")
    assert response.status_code == 200
    assert response.json()["app_name"] == APP_NAME
