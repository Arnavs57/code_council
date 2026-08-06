"""Rate-limiting middleware — PLACEHOLDER ONLY.

Phase 2 will enforce per-tenant / per-key limits backed by Redis
(sliding-window counters) and return ``429`` with a ``Retry-After`` header.
TODO(phase-2): Redis client, window logic, quota config from settings.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RateLimitingPlaceholderMiddleware(BaseHTTPMiddleware):
    """Placeholder: passes every request through unchanged."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)
