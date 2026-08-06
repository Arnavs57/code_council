"""Request-ID middleware (outermost).

Assigns (or propagates) a request id, exposes it on ``request.state`` and in
the response header, and pushes it into the logging context so every log
record produced for the request carries it.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core import constants
from app.logs import context as logs_context


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ensure every request has a stable id for tracing and support."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        incoming = request.headers.get(constants.HEADER_REQUEST_ID)
        request_id = incoming or uuid.uuid4().hex
        request.state.request_id = request_id
        token = logs_context.set_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            logs_context.reset_request_id(token)
        response.headers[constants.HEADER_REQUEST_ID] = request_id
        return response
