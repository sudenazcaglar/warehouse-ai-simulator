import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.errors import ErrorDetail, ErrorResponse, ValidationErrorDetail

logger = logging.getLogger("warehouse_api.errors")


class APIError(Exception):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


class BadRequestError(APIError):
    def __init__(
        self,
        message: str = "Bad request.",
        code: str = "bad_request",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=code,
            message=message,
            details=details,
        )


class NotFoundError(APIError):
    def __init__(
        self,
        message: str = "Resource not found.",
        code: str = "not_found",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code=code,
            message=message,
            details=details,
        )


class ConflictError(APIError):
    def __init__(
        self,
        message: str = "Resource conflict.",
        code: str = "conflict",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            code=code,
            message=message,
            details=details,
        )


class DatabaseOperationError(APIError):
    def __init__(
        self,
        message: str = "Database operation failed.",
        code: str = "database_error",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code=code,
            message=message,
            details=details,
        )


def get_request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def build_error_response(
    *,
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    request_id = get_request_id(request)

    payload = ErrorResponse(
        error=ErrorDetail(
            code=code,
            message=message,
            details=details or {},
            request_id=request_id,
        )
    )

    headers = {}
    if request_id:
        headers["X-Request-ID"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=jsonable_encoder(payload),
        headers=headers,
    )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    logger.warning(
        "api_error request_id=%s status_code=%s code=%s message=%s",
        get_request_id(request),
        exc.status_code,
        exc.code,
        exc.message,
    )

    return build_error_response(
        request=request,
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    code = "not_found" if exc.status_code == status.HTTP_404_NOT_FOUND else "http_error"
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error."

    logger.warning(
        "http_error request_id=%s status_code=%s path=%s message=%s",
        get_request_id(request),
        exc.status_code,
        request.url.path,
        message,
    )

    return build_error_response(
        request=request,
        status_code=exc.status_code,
        code=code,
        message=message,
        details={},
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    validation_errors = [
        ValidationErrorDetail(
            location=list(error.get("loc", [])),
            message=str(error.get("msg", "")),
            error_type=str(error.get("type", "")),
        ).model_dump()
        for error in exc.errors()
    ]

    logger.warning(
        "validation_error request_id=%s path=%s errors=%s",
        get_request_id(request),
        request.url.path,
        len(validation_errors),
    )

    return build_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="Request validation failed.",
        details={"errors": validation_errors},
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    logger.exception(
        "database_error request_id=%s path=%s error=%s",
        get_request_id(request),
        request.url.path,
        exc.__class__.__name__,
    )

    return build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="database_error",
        message="Database operation failed.",
        details={},
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception(
        "unhandled_error request_id=%s path=%s error=%s",
        get_request_id(request),
        request.url.path,
        exc.__class__.__name__,
    )

    return build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        message="Internal server error.",
        details={},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
