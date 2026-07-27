"""
全局异常捕获中间件

捕获未处理的异常，返回统一格式的错误响应。
"""

import traceback

import structlog
from fastapi import Request
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.responses.Base import ApiResponse
from config.db import get_settings

LOGGER = structlog.get_logger(__name__)


class CatchErrorMiddleware(BaseHTTPMiddleware):
    """全局异常捕获中间件"""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: callable) -> ORJSONResponse:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            return await _handle_exception(request, e)


async def _handle_exception(request: Request, exc: Exception) -> ORJSONResponse:
    """处理异常并返回统一格式"""
    settings = get_settings()

    # 记录错误日志
    LOGGER.bind(
        path=str(request.url),
        method=request.method,
        error=str(exc),
        traceback=traceback.format_exc(),
    ).error("Unhandled exception")

    # 开发环境返回详细错误
    if settings.DEBUG:
        return ORJSONResponse(
            content=ApiResponse(
                code=500,
                message=str(exc),
                data={"traceback": traceback.format_exc().split("\n")} if settings.DEBUG else None,
            ).model_dump(),
            status_code=500,
        )

    # 生产环境返回通用错误
    return ORJSONResponse(
        content=ApiResponse(
            code=500,
            message="internal server error",
        ).model_dump(),
        status_code=500,
    )


async def global_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    """FastAPI 异常处理器 — 用于 add_exception_handler"""
    return await _handle_exception(request, exc)
