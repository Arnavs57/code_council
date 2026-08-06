"""Global exception handlers — every error leaves the API as consistent JSON.

Envelope: ``{"error": {"code", "message", "request_id"}}`` (+ optional
``details`` for validation errors). Internal exception text is never leaked
to clients.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import AppError
from app.core.responses import error_response
from app.logs.context import get_request_id

logger = logging.getLogger("app.error")


def _request_id(request: Request) -> str | None:
    """Best-effort request id: middleware state first, contextvar fallback."""
    return getattr(request.state, "request_id", None) or get_request_id()


async def _validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = _request_id(request)
    logger.warning(
        "validation_error",
        extra={"error_code": "VALIDATION_ERROR", "request_id": request_id},
    )
    details = [
        {
            "location": ".".join(str(part) for part in err.get("loc", [])),
            "message": err.get("msg", ""),
        }
        for err in exc.errors()
    ]
    content = error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed.",
        request_id=request_id,
    )
    content["error"]["details"] = details
    return JSONResponse(status_code=422, content=content)


async def _http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    request_id = _request_id(request)
    # 4xx (including 404 probes from bots) are noise, not incidents: log at
    # INFO. 5xx are operational signals: log at WARNING.
    log = logger.warning if exc.status_code >= 500 else logger.info
    log(
        "http_error",
        extra={"error_code": f"HTTP_{exc.status_code}", "request_id": request_id},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=f"HTTP_{exc.status_code}",
            message=str(exc.detail),
            request_id=request_id,
        ),
    )


async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = _request_id(request)
    logger.error(
        "app_error",
        extra={
            "error_code": exc.code,
            "status_code": exc.status_code,
            "request_id": request_id,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(
            code=exc.code,
            message=exc.message,
            request_id=request_id,
        ),
    )


async def _unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    request_id = _request_id(request)
    logger.exception("unhandled_exception", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content=error_response(
            code="INTERNAL_ERROR",
            message="An internal error occurred.",
            request_id=request_id,
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every global handler to the application."""
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_exception_handler)
    app.add_exception_handler(AppError, _app_error_handler)
    app.add_exception_handler(Exception, _unhandled_exception_handler)
