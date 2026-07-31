"""
测试配置 — pytest fixtures

pytest-asyncio 1.x: 通过 pyproject.toml 的
`asyncio_default_fixture_loop_scope = "session"` 和
`asyncio_default_test_loop_scope = "session"` 让所有 async fixture 与测试
共享同一个 session 级 event loop，避免 Tortoise ORM 连接在不同 loop 间
切换重建（Tortoise 1.x 在此场景下可能挂起）。

使用 sqlite 临时文件作为测试数据库（:memory: 在不同 event loop 间不共享）。
"""

import os
import tempfile
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

# 测试用 Tortoise 配置（临时文件，避免 :memory: 的 loop 切换问题）
_TEST_DB_FILE = os.path.join(tempfile.gettempdir(), "axhub_test.db")
if os.path.exists(_TEST_DB_FILE):
    os.remove(_TEST_DB_FILE)

TEST_TORTOISE_CONFIG = {
    "connections": {
        "default": f"sqlite://{_TEST_DB_FILE}",
    },
    "apps": {
        "models": {
            "models": [
                "models.project",
                "models.prototype",
                "models.annotation",
                "models.knowledge",
                "models.publish",
                "models.media",
                "models.document",
                "models.template_library",
                "models.review_artifact",
                "models.review_report",
                "models.access_control",
                "models.cloud_publish",
                "models.ai_runtime",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    """初始化测试数据库（session 级，运行在 session event loop 上）"""
    await Tortoise.init(config=TEST_TORTOISE_CONFIG)
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """httpx 异步测试客户端"""
    from main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
