"""
API Key 认证中间件

用于 API 端点的认证保护。
支持 Header 和 Query Parameter 两种方式。
"""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.db import get_settings

# 不需要认证的路径
PUBLIC_PATHS = {
    "/health",
    "/health/detailed",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
}


class TokenMiddleware(BaseHTTPMiddleware):
    """API Key 认证中间件"""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: callable) -> callable:
        # 公开路径跳过认证
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        # 开发模式跳过认证
        settings = get_settings()
        if settings.DEBUG:
            return await call_next(request)

        # 从 Header 或 Query 获取 API Key
        api_key = request.headers.get("X-API-Key", "")
        if not api_key:
            api_key = request.query_params.get("api_key", "")

        if not api_key or api_key != settings.API_KEY:
            raise HTTPException(status_code=401, detail="Invalid or missing API Key")

        return await call_next(request)


# 可选: 用于路由依赖的 API Key 校验
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = None,
) -> str | None:
    """依赖注入: 验证 Bearer Token

    用法:
        @router.get("/protected")
        async def protected(api_key: str = Depends(verify_api_key)):
            ...
    """
    settings = get_settings()
    if settings.DEBUG:
        return settings.API_KEY

    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing authorization")

    if credentials.credentials != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    return credentials.credentials
