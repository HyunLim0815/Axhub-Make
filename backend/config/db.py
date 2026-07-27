"""
数据库配置 — pydantic-settings

从 .env 文件或环境变量读取数据库和中间件配置。
"""

from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库 + 应用配置"""

    # 应用
    APP_NAME: str = "axhub-make-backend"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # 数据库 (PostgreSQL)
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "axhub"
    DB_PASSWORD: str = "axhub_secret"
    DB_NAME: str = "axhub_make"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AI
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-4o"
    AI_SIMPLE_MODEL: str = "gpt-4o-mini"
    AI_COMPLEX_MODEL: str = "o3-mini"

    # 监控
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    PROMETHEUS_ENABLED: bool = True

    # 安全
    API_KEY: str = "axhub-dev-key"
    CORS_ORIGINS: list[str] = ["*"]

    # 日志
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        """构建 PostgreSQL 连接 URL"""
        return (
            f"postgres://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


_settings: DatabaseSettings | None = None


def get_settings() -> DatabaseSettings:
    """获取配置单例"""
    global _settings
    if _settings is None:
        _settings = DatabaseSettings()
    return _settings
