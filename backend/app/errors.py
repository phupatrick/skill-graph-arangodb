"""Lỗi API thống nhất theo hợp đồng:

    { "error": { "code": "NOT_FOUND", "message": "..." } }

Frontend chỉ cần kiểm tra `body.error.code` là xử lý được mọi trường hợp,
thay vì mỗi endpoint trả một kiểu lỗi khác nhau.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class ApiError(Exception):
    """Lỗi nghiệp vụ có mã lỗi ổn định cho client."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        *,
        details: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def not_found(kind: str, identifier: str) -> ApiError:
    return ApiError(
        404,
        "NOT_FOUND",
        f"Không tìm thấy {kind} với id '{identifier}'.",
        details={"kind": kind, "id": identifier},
    )


def bad_request(message: str, **details: object) -> ApiError:
    return ApiError(400, "BAD_REQUEST", message, details=dict(details))


def conflict(message: str, **details: object) -> ApiError:
    return ApiError(409, "CONFLICT", message, details=dict(details))


def _envelope(code: str, message: str, details: dict | None = None) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api_error(_: Request, exc: ApiError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=_envelope(
                "VALIDATION_ERROR",
                "Dữ liệu gửi lên không hợp lệ.",
                {"errors": exc.errors()},
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}.get(
            exc.status_code, "HTTP_ERROR"
        )
        return JSONResponse(
            status_code=exc.status_code, content=_envelope(code, str(exc.detail))
        )

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        # Không lộ stack trace / mật khẩu DB ra ngoài.
        return JSONResponse(
            status_code=500,
            content=_envelope(
                "INTERNAL_ERROR",
                "Lỗi máy chủ không mong đợi. Xem log của uvicorn để biết chi tiết.",
            ),
        )
