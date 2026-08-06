"""Middleware registration.

Starlette semantics: the LAST middleware registered is the OUTERMOST (it sees
the request first). The registration order below therefore mirrors execution
order from outside-in. Keep it deliberate — reordering changes behavior.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import Settings
from app.core import constants
from app.middleware.authentication import AuthenticationPlaceholderMiddleware
from app.middleware.logging import AccessLogMiddleware
from app.middleware.rate_limiting import RateLimitingPlaceholderMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.security_headers import SecurityHeadersPlaceholderMiddleware
from app.middleware.timing import RequestTimingMiddleware


def register_middleware(app: FastAPI, settings: Settings) -> None:
    """Attach the middleware stack. Execution order (outermost first):

    0. CORS            — handle cross-origin + preflight requests
    1. RequestID       — assign/propagate request id (logs carry it)
    2. AccessLog       — one structured log line per request
    3. SecurityHeaders — placeholder (Phase 2: security header policy)
    4. RequestTiming   — record start time for future metrics
    5. RateLimiting    — placeholder (Phase 2: Redis-backed limits)
    6. Authentication  — placeholder (Phase 2: JWT/RBAC)
    """
    # Innermost-first registration (Starlette wraps in reverse order), so the
    # list below reads outermost → innermost.
    app.add_middleware(AuthenticationPlaceholderMiddleware)
    app.add_middleware(RateLimitingPlaceholderMiddleware)
    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(SecurityHeadersPlaceholderMiddleware)
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # CORS must be outermost so preflight (OPTIONS) requests are answered
    # with the right headers before any other middleware sees them.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.core.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[constants.HEADER_REQUEST_ID],
    )


__all__ = ["register_middleware"]
