"""
测试配置 — pytest fixtures

使用 sqlite://:memory: 作为测试数据库。
"""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

# 测试用 Tortoise 配置
TEST_TORTOISE_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": ":memory:"},
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
}


@pytest.fixture(scope="session")
def event_loop():
    """session 级事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def initialize_db():
    """初始化测试数据库"""
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
