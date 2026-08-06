"""Access-log middleware: one structured log line per request."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.access")


class AccessLogMiddleware(BaseHTTPMiddleware):
    """Log method, path, status and duration for every request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            # Always emit the access line — including when the downstream
            # raised (status stays 500) — so every request is accounted for.
            duration_ms = (time.perf_counter() - start) * 1000.0
            logger.info(
                "http_request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 3),
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
