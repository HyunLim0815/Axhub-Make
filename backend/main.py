"""
Axhub Make — FastAPI 应用入口

遵循 fastapi-guider 规范:
- Tortoise ORM + asyncpg (PostgreSQL)
- Loguru + structlog 结构化日志
- Prometheus + Sentry 监控
- SlowAPI 限流 + secure 安全头
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

import sentry_sdk
import structlog
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from config.db import get_settings
from config.tortoise import get_tortoise_config
from middlewares.catch_error import CatchErrorMiddleware, global_exception_handler
from utils.tools.logger import configure_logging

settings = get_settings()
LOGGER = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理"""
    # 启动时
    configure_logging()

    from config.tortoise import init_tortoise, close_tortoise
    register = await init_tortoise(app)
    app.state.tortoise_register = register
    LOGGER.bind(mode="sqlite" if settings.DEBUG else "postgres").info("Database connected")

    # 初始化 Sentry
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            integrations=[
                FastApiIntegration(),
                LoggingIntegration(level=settings.LOG_LEVEL.upper()),
            ],
        )
        LOGGER.info("Sentry initialized")

    yield

    # 关闭时
    if hasattr(app.state, 'tortoise_register'):
        from config.tortoise import close_tortoise
        await close_tortoise(app.state.tortoise_register)
    LOGGER.info("Database connections closed")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── 中间件注册 (顺序重要) ──

# 1. 请求追踪 ID
app.add_middleware(CorrelationIdMiddleware)

# 2. CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 限流
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 4. 全局异常捕获
app.add_middleware(CatchErrorMiddleware)
app.add_exception_handler(Exception, global_exception_handler)

# Prometheus 指标
if get_settings().PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# ── 健康检查 ──

@app.get("/health", tags=["system"])
async def health_check() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/health/detailed", tags=["system"])
async def health_detailed() -> dict:
    """详细健康检查 — 数据库 + 缓存状态"""
    from tortoise import Tortoise

    db_ok = True
    redis_ok = True

    try:
        from tortoise.connection import connections
        conn = connections.get("default")
        await conn.execute_query("SELECT 1")
    except Exception:
        db_ok = False

    try:
        from redis import Redis
        from config.db import get_settings

        s = get_settings()
        r = Redis.from_url(s.REDIS_URL)
        r.ping()
        r.close()
    except Exception:
        redis_ok = False

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
        "redis": "connected" if redis_ok else "disconnected",
    }


# ── 路由注册 ──

from api.router.v1 import annotations, knowledge, projects, prototypes, publish, ai

app.include_router(projects.router)
app.include_router(prototypes.router)
app.include_router(annotations.router)
app.include_router(knowledge.router)
app.include_router(publish.router)
app.include_router(ai.router)
