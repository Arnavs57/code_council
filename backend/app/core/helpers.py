"""Small, dependency-free helpers shared across the codebase."""

import uuid
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat()


def generate_id() -> str:
    """Generate a random, URL-safe identifier (e.g. request IDs)."""
    return uuid.uuid4().hex


def split_csv(value: str) -> list[str]:
    """Split a comma-separated string into a cleaned list of items."""
    return [item.strip() for item in value.split(",") if item.strip()]
