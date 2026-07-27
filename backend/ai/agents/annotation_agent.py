"""
标注执行 Agent — LangGraph 工作流

流程: 分析需求 → 制定计划 → 执行修改 → 验证结果
"""

from typing import Any, AsyncIterator, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from ai.agents.base import BaseAgent

LOGGER = structlog.get_logger(__name__)

ANNOTATION_SYSTEM_PROMPT = """你是一个产品标注助手。根据用户对页面元素的描述，生成简洁准确的标注说明。
标注应当清晰说明该元素的功能、状态和交互方式。"""


class AnnotationState(TypedDict):
    """标注执行状态"""
    prompt: str
    element_info: dict[str, Any]
    analysis: str
    plan: str
    annotation_text: str
    verified: bool
    retry_count: int


MAX_RETRY = 3


class AnnotationAgent(BaseAgent):
    """标注执行 Agent"""

    def __init__(self) -> None:
        super().__init__()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AnnotationState)
        builder.add_node("analyze", self._analyze)
        builder.add_node("draft", self._draft)
        builder.add_node("verify", self._verify)
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "draft")
        builder.add_edge("draft", "verify")
        builder.add_conditional_edges(
            "verify",
            self._decide_next,
            {"accept": END, "retry": "draft", "abort": END},
        )
        return builder.compile()

    async def _analyze(self, state: AnnotationState) -> dict:
        LOGGER.bind(prompt=state["prompt"][:50]).info("Analyzing annotation request")
        analysis = await self._llm_call(
            ANNOTATION_SYSTEM_PROMPT,
            f"分析以下标注需求：\n用户需求：{state['prompt']}\n\n"
            f"元素信息：{state.get('element_info', {})}",
        )
        return {"analysis": analysis}

    async def _draft(self, state: AnnotationState) -> dict:
        LOGGER.info("Drafting annotation")
        annotation = await self._llm_call(
            ANNOTATION_SYSTEM_PROMPT,
            f"基于分析结果生成标注内容：\n{state['analysis']}",
        )
        return {"annotation_text": annotation}

    async def _verify(self, state: AnnotationState) -> dict:
        LOGGER.bind(retry=state.get("retry_count", 0)).info("Verifying annotation")
        verification = await self._llm_call(
            "你是一个质量检查员。检查以下标注是否准确地反映了需求。"
            "如果准确，回复 ACCEPT；如果需要改进，回复改进建议。",
            f"需求：{state['prompt']}\n\n生成的标注：{state.get('annotation_text', '')}",
        )
        is_accepted = "ACCEPT" in verification.upper()
        return {"verified": is_accepted}

    def _decide_next(self, state: AnnotationState) -> str:
        if state.get("verified"):
            return "accept"
        retry = (state.get("retry_count") or 0) + 1
        state["retry_count"] = retry
        if retry >= MAX_RETRY:
            LOGGER.warning("Max retry reached")
            return "abort"
        return "retry"

    async def run(self, prompt: str, element_info: dict[str, Any] | None = None) -> str:
        """执行标注生成"""
        LOGGER.bind(prompt=prompt[:50]).info("AnnotationAgent started")
        state: AnnotationState = {
            "prompt": prompt,
            "element_info": element_info or {},
            "analysis": "",
            "plan": "",
            "annotation_text": "",
            "verified": False,
            "retry_count": 0,
        }
        async for _ in self.graph.astream(state):
            pass
        return state.get("annotation_text", "") or state.get("analysis", "")
