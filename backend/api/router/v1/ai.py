"""AI API 路由 — SSE 流式 + Context Bundle + Prompt Pack"""

from fastapi import APIRouter, Query

from ai.context_bundle import ContextBundle, PromptPack
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
async def get_context(prototype_id: int | None = Query(None)):
    """获取 Context Bundle (结构化上下文)"""
    bundle = await ContextBundle.build(prototype_id)
    return ApiResponse(data=bundle)


@router.get("/prompt-pack")
async def get_prompt_pack(
    role: str = Query("engineering", pattern="^(engineering|testing|review)$"),
    prototype_id: int | None = Query(None),
):
    """获取角色 Prompt 包

    Args:
        role: engineering | testing | review
        prototype_id: 可选原型 ID
    """
    prompt = await PromptPack.generate(role, prototype_id)
    return ApiResponse(data={"role": role, "prompt": prompt})
