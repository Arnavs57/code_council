"""Root endpoint: application information."""

from fastapi import APIRouter

from app.config.config import settings
from app.core.responses import infrastructure_status

router = APIRouter(tags=["infrastructure"])


@router.get("/", summary="Application information")
async def root() -> dict[str, str]:
    """Return basic application metadata (name, version, status, env, time)."""
    core = settings.core
    return infrastructure_status(
        app_name=core.app_name,
        version=core.app_version,
        environment=core.environment,
    )
