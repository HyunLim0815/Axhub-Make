"""
LLM 服务 — OpenAI SDK 封装

支持流式和非流式两种调用方式。
兼容任何 OpenAI 兼容 API (OpenAI, Claude, DeepSeek 等)。
"""

from typing import AsyncIterator

import structlog
from openai import AsyncOpenAI

from config.db import get_settings

LOGGER = structlog.get_logger(__name__)


class LLMService:
    """LLM 调用服务"""

    def __init__(self) -> None:
        settings = get_settings()
        self.client = AsyncOpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )
        self.default_model = settings.AI_MODEL
        self.simple_model = settings.AI_SIMPLE_MODEL
        self.complex_model = settings.AI_COMPLEX_MODEL

    async def chat(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> str:
        """非流式调用 — 返回完整文本

        Args:
            messages: OpenAI 格式的消息列表
            model: 模型名称，默认使用 AI_MODEL

        Returns:
            模型返回的文本内容
        """
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,  # type: ignore
        )
        content = response.choices[0].message.content or ""
        LOGGER.bind(
            model=model or self.default_model,
            input_tokens=response.usage.prompt_tokens if response.usage else 0,
            output_tokens=response.usage.completion_tokens if response.usage else 0,
        ).debug("LLM chat completed")
        return content

    async def chat_stream(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """流式调用 — 逐 token 产出

        Args:
            messages: OpenAI 格式的消息列表
            model: 模型名称

        Yields:
            每个文本块
        """
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,  # type: ignore
            stream=True,
        )
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
