"""Code Council AI — FastAPI application entry point.

Start with::

    uvicorn app.main:app --reload

Run from the ``backend/`` directory.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.v1.router import api_v1_router, infra_router
from app.config.audit import log_config_audit
from app.config.config import settings
from app.database.database import init_db
from app.logs.config import setup_logging
from app.middleware import register_middleware

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle: initializes logging, database, and configuration audit at boot."""
    setup_logging(settings)
    log_config_audit(settings)
    init_db()

    logger.info("startup_begin", extra={"environment": settings.core.environment})
    logger.info("startup_complete", extra={"environment": settings.core.environment})
    yield
    logger.info("shutdown_begin", extra={"environment": settings.core.environment})
    logger.info("shutdown_complete", extra={"environment": settings.core.environment})


def create_app() -> FastAPI:
    """Application factory — keeps imports lazy and testing clean."""
    core = settings.core

    app = FastAPI(
        title=core.app_name,
        description=core.app_description,
        version=core.app_version,
        lifespan=lifespan,
        openapi_tags=[
            {
                "name": "infrastructure",
                "description": "Platform infrastructure endpoints (root, health, version).",
            },
            {
                "name": "github",
                "description": "GitHub Pull Request Webhooks & Action triggers.",
            },
        ],
        docs_url="/docs" if core.docs_enabled else None,
        redoc_url="/redoc" if core.docs_enabled else None,
        openapi_url="/openapi.json" if core.docs_enabled else None,
    )

    register_middleware(app, settings=settings)
    register_exception_handlers(app)

    # Infrastructure routes (root /, /health, /version)
    app.include_router(infra_router)
    # API v1 domain routes (/api/v1/github/event, etc.)
    app.include_router(api_v1_router, prefix=settings.core.api_v1_prefix)

    return app


app = create_app()
