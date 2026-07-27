"""
Redis 缓存工具 — 连接池 + 装饰器

使用 orjson 进行二进制序列化。
支持装饰器和直接调用两种方式。
"""

import functools
from typing import Any, Callable, Optional

import orjson
import structlog
from redis import asyncio as aioredis

from config.db import get_settings

LOGGER = structlog.get_logger(__name__)

_pool: aioredis.ConnectionPool | None = None


async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接（连接池模式）"""
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = aioredis.ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=20,
            decode_responses=False,
        )
        LOGGER.info("Redis connection pool created")
    return aioredis.Redis(connection_pool=_pool)


async def close_redis() -> None:
    """关闭 Redis 连接池"""
    global _pool
    if _pool:
        await _pool.disconnect()
        _pool = None
        LOGGER.info("Redis connection pool closed")


def cached(expire: int = 300, prefix: str = "cache") -> Callable:
    """
    Redis 缓存装饰器

    Args:
        expire: 过期时间（秒），默认 5 分钟
        prefix: 缓存键前缀

    用法:
        @cached(expire=600, prefix="annotation")
        async def get_annotation(id: int): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 构建缓存键
            key_parts = [prefix, func.__name__]
            key_parts.extend(str(a) for a in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            try:
                redis = await get_redis()
                cached_data = await redis.get(cache_key)
                if cached_data:
                    LOGGER.bind(cache_key=cache_key).debug("Cache hit")
                    return orjson.loads(cached_data)
            except Exception as e:
                LOGGER.bind(error=str(e)).warning("Cache read failed")

            # 执行原函数
            result = await func(*args, **kwargs)

            # 写入缓存
            try:
                redis = await get_redis()
                await redis.setex(cache_key, expire, orjson.dumps(result))
                LOGGER.bind(cache_key=cache_key, expire=expire).debug("Cache set")
            except Exception as e:
                LOGGER.bind(error=str(e)).warning("Cache write failed")

            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str) -> None:
    """按模式清除缓存

    Args:
        pattern: 键模式，如 "annotation:*"

    用法:
        await invalidate_cache("annotation:*")
    """
    try:
        redis = await get_redis()
        cursor = 0
        deleted = 0
        while True:
            cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await redis.delete(*keys)
                deleted += len(keys)
            if cursor == 0:
                break
        if deleted:
            LOGGER.bind(pattern=pattern, deleted=deleted).info("Cache invalidated")
    except Exception as e:
        LOGGER.bind(error=str(e)).warning("Cache invalidation failed")
