"""
Agent 基类 — 共享的 LangGraph 工作流工具
"""

from typing import Any, AsyncIterator

import structlog

from ai.llm import LLMService
from ai.router import ModelRouter

LOGGER = structlog.get_logger(__name__)


class BaseAgent:
    """Agent 基类 — 所有 Agent 继承此类"""

    def __init__(self, llm: LLMService | None = None) -> None:
        self.llm = llm or LLMService()
        self.router = ModelRouter()

    async def _llm_call(
        self,
        system_prompt: str,
        user_prompt: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """LLM 调用（自动路由模型）"""
        model = self.router.route(user_prompt, context)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self.llm.chat(messages, model=model)

    async def _llm_stream(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AsyncIterator[str]:
        """流式 LLM 调用"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        async for chunk in self.llm.chat_stream(messages):
            yield chunk
