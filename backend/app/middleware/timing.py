"""Request-timing middleware — PLACEHOLDER.

Records the request start time on ``request.state`` so a future metrics
pipeline has a stable hook. Duration is already logged by the access-log
middleware. TODO(phase-2): expose per-route timings to a metrics backend.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Placeholder: stores the request start time on ``request.state``."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request.state.start_time = time.perf_counter()
        return await call_next(request)
