"""Tortoise ORM 配置 + FastAPI 中间件封装

开发环境用 SQLite，生产用 PostgreSQL。
提供 get_tortoise_config() 和 TortoiseMiddleware 两个导出。
"""

from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

from config.db import get_settings


def get_tortoise_config() -> dict:
    """获取 Tortoise ORM 完整配置"""
    settings = get_settings()
    use_sqlite = settings.DEBUG

    if use_sqlite:
        return {
            "connections": {
                "default": "sqlite://data/axhub.db",
            },
            "apps": {
                "models": {
                    "models": [
                        "models.project",
                        "models.prototype",
                        "models.annotation",
                        "models.knowledge",
                        "models.publish",
                    ],
                    "default_connection": "default",
                }
            },
            "use_tz": True,
            "timezone": "Asia/Shanghai",
        }

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": settings.DB_HOST,
                    "port": settings.DB_PORT,
                    "user": settings.DB_USER,
                    "password": settings.DB_PASSWORD,
                    "database": settings.DB_NAME,
                },
            }
        },
        "apps": {
            "models": {
                "models": [
                    "models.prototype",
                    "models.annotation",
                    "models.knowledge",
                    "models.publish",
                ],
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "Asia/Shanghai",
    }


async def init_tortoise(app):
    """初始化 Tortoise ORM（在 FastAPI lifespan 中调用）"""
    config = get_tortoise_config()
    register = RegisterTortoise(
        app=app,
        config=config,
        generate_schemas=True,
        _enable_global_fallback=True,
    )
    await register.__aenter__()
    return register


async def close_tortoise(register):
    """关闭 Tortoise ORM"""
    await register.__aexit__(None, None, None)
