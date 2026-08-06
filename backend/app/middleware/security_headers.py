"""Security-headers middleware — PLACEHOLDER ONLY.

Phase 2 will add the production header policy:
  * ``X-Content-Type-Options: nosniff``
  * ``X-Frame-Options: DENY``
  * ``Content-Security-Policy`` (configurable, origin-aware)
  * ``Strict-Transport-Security`` (production only, behind TLS)

TODO(phase-2): header policy driven by settings.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersPlaceholderMiddleware(BaseHTTPMiddleware):
    """Placeholder: passes every request through unchanged."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)
