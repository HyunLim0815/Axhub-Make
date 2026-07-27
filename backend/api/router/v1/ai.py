"""AI API 路由 — SSE 流式 + Context Bundle"""

from fastapi import APIRouter, Depends

from ai.llm import LLMService
from api.responses.Base import ApiResponse
from utils.tools.sse import create_sse_response

router = APIRouter(prefix="/v1/ai", tags=["ai"])


@router.get("/health")
async def ai_health():
    """AI 服务健康检查"""
    return ApiResponse(data={"status": "ok", "provider": "openai-compatible"})


@router.post("/chat")
async def chat(prompt: str, system_prompt: str | None = None):
    """非流式对话"""
    llm = LLMService()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    result = await llm.chat(messages)
    return ApiResponse(data={"content": result})


@router.post("/chat/stream")
async def chat_stream(prompt: str, system_prompt: str | None = None):
    """流式对话 (SSE)"""
    llm = LLMService()
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return create_sse_response(llm.chat_stream(messages))


@router.get("/context")
async def get_context(prototype_id: int | None = None):
    """获取项目上下文（知识库摘要）"""
    from api.controllers.KnowledgeController import KnowledgeController

    entries = await KnowledgeController.get_list(page=1, size=20)
    context = "# 项目知识库\n\n"
    for entry in entries[0]:
        context += f"- **{entry.title}** ({entry.type}): {entry.content[:200]}\n"

    return ApiResponse(data={"context": context})
