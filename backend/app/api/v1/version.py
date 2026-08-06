"""Version endpoint."""

from fastapi import APIRouter

from app.config.config import settings
from app.core.responses import infrastructure_status

router = APIRouter(tags=["infrastructure"])


@router.get("/version", summary="Application version")
async def version() -> dict[str, str]:
    """Return the running application version."""
    core = settings.core
    return infrastructure_status(
        app_name=core.app_name,
        version=core.app_version,
        environment=core.environment,
    )
