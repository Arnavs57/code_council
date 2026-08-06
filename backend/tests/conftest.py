"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client() -> TestClient:
    """TestClient exercising the real application (middleware + lifespan).

    Using it as a context manager triggers the lifespan startup/shutdown
    events, so those are verified by every test that uses it.
    """
    with TestClient(app) as test_client:
        yield test_client
