"""Health-check endpoint."""

from fastapi import APIRouter

from app.config.config import settings
from app.core.responses import infrastructure_status
from app.llm import get_llm_service

router = APIRouter(tags=["infrastructure"])


@router.get("/health", summary="Liveness check")
async def health() -> dict[str, str]:
    """Return ``200`` while the process is alive and serving requests.

    Future phases will extend this into a readiness check that also probes
    the database, event bus and worker queues.
    """
    core = settings.core
    return infrastructure_status(
        app_name=core.app_name,
        version=core.app_version,
        environment=core.environment,
    )


@router.get("/health/llm", summary="LLM provider readiness")
async def llm_health() -> dict:
    """Probe the configured provider without producing a model completion."""
    return get_llm_service().health_check()
