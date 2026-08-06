"""Version-1 API routers — separates root infrastructure endpoints from API v1 domain endpoints."""

from fastapi import APIRouter

from app.api.v1 import github, health, root, version

# Infrastructure endpoints mounted at root for ops/health checks
infra_router = APIRouter(tags=["infrastructure"])
infra_router.include_router(root.router)
infra_router.include_router(health.router)
infra_router.include_router(version.router)

# Version 1 domain API router mounted at /api/v1
api_v1_router = APIRouter()
api_v1_router.include_router(infra_router)
api_v1_router.include_router(github.router)
