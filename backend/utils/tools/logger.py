"""
日志配置 — Loguru + structlog

生产: INFO 级别, JSON 格式, 日志轮转
开发: DEBUG 级别, 彩色控制台输出
"""

import sys

import structlog
from loguru import logger as loguru_logger

from config.db import get_settings


def configure_logging() -> None:
    """配置 Loguru + structlog"""
    settings = get_settings()
    log_level = settings.LOG_LEVEL.upper() if not settings.DEBUG else "DEBUG"

    # 移除默认 handler
    loguru_logger.remove()

    if settings.DEBUG:
        # 开发: 彩色控制台
        loguru_logger.add(
            sys.stdout,
            level=log_level,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "<level>{message}</level>"
            ),
            colorize=True,
        )
    else:
        # 生产: JSON + 轮转
        loguru_logger.add(
            "logs/axhub-{time:YYYY-MM-DD}.log",
            level=log_level,
            format="{time} | {level} | {name}:{function}:{line} | {message}",
            rotation="500 MB",
            retention="30 days",
            compression="zip",
        )

    # 配置 structlog 使用 Loguru 作为后端
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer() if settings.DEBUG
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
