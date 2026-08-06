"""Authentication middleware — PLACEHOLDER ONLY.

No logic is implemented in Phase 1. The future JWT/RBAC flow will verify
bearer tokens here (or via FastAPI dependencies) and attach the
authenticated principal to ``request.state.user`` before routes run.
TODO(phase-2): token verification, principal resolution, deny-by-default.
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class AuthenticationPlaceholderMiddleware(BaseHTTPMiddleware):
    """Placeholder: passes every request through unchanged."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        return await call_next(request)
