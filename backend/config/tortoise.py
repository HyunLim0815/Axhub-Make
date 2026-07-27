"""
Tortoise ORM 配置

提供 Tortoise-ORM 初始化所需的配置字典。
模型注册路径: models.prototype, models.annotation, models.knowledge, models.publish
"""

from config.db import get_settings


def get_tortoise_config() -> dict:
    """获取 Tortoise ORM 完整配置"""
    settings = get_settings()
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
                    "aerich.models",  # 迁移管理
                ],
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "Asia/Shanghai",
    }
