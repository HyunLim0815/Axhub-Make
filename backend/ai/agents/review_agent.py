"""
审查 Agent — 多维度原型审查

流程: 功能审查 → 安全审查 → UX 审查 → 汇总报告
"""

from typing import Any, AsyncIterator, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from ai.agents.base import BaseAgent

LOGGER = structlog.get_logger(__name__)


class ReviewState(TypedDict):
    """审查状态"""
    target: str
    context: str
    function_review: str
    security_review: str
    ux_review: str
    summary: str


class ReviewAgent(BaseAgent):
    """多维度审查 Agent"""

    def __init__(self) -> None:
        super().__init__()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(ReviewState)
        builder.add_node("review_function", self._review_function)
        builder.add_node("review_security", self._review_security)
        builder.add_node("review_ux", self._review_ux)
        builder.add_node("summarize", self._summarize)
        builder.set_entry_point("review_function")
        builder.add_edge("review_function", "review_security")
        builder.add_edge("review_security", "review_ux")
        builder.add_edge("review_ux", "summarize")
        builder.add_edge("summarize", END)
        return builder.compile()

    async def _review_function(self, state: ReviewState) -> dict:
        LOGGER.info("Reviewing functionality")
        review = await self._llm_call(
            "你是一个功能审查专家。检查以下内容是否满足功能需求，"
            "是否有遗漏的功能点或逻辑错误。",
            f"目标：{state['target']}\n\n上下文：{state['context']}",
        )
        return {"function_review": review}

    async def _review_security(self, state: ReviewState) -> dict:
        LOGGER.info("Reviewing security")
        review = await self._llm_call(
            "你是一个安全审查专家。检查以下内容是否存在安全风险，"
            "包括数据泄露、权限缺失、输入验证不足等。",
            f"目标：{state['target']}\n\n功能审查结论：{state.get('function_review', '')}",
        )
        return {"security_review": review}

    async def _review_ux(self, state: ReviewState) -> dict:
        LOGGER.info("Reviewing user experience")
        review = await self._llm_call(
            "你是一个 UX 审查专家。评估以下内容的用户体验，"
            "包括交互流程、信息架构、一致性和可访问性。",
            f"目标：{state['target']}",
        )
        return {"ux_review": review}

    async def _summarize(self, state: ReviewState) -> dict:
        LOGGER.info("Generating summary report")
        summary = await self._llm_call(
            "你是一个审查报告撰写专家。将以下三个维度的审查结果汇总为简明报告。",
            f"## 功能审查\n{state.get('function_review', '无')}\n\n"
            f"## 安全审查\n{state.get('security_review', '无')}\n\n"
            f"## UX 审查\n{state.get('ux_review', '无')}",
        )
        return {"summary": summary}

    async def run(
        self,
        target: str,
        context: str | None = None,
    ) -> dict[str, str]:
        """执行多维度审查"""
        LOGGER.bind(target=target[:50]).info("ReviewAgent started")
        state: ReviewState = {
            "target": target,
            "context": context or "",
            "function_review": "",
            "security_review": "",
            "ux_review": "",
            "summary": "",
        }
        async for _ in self.graph.astream(state):
            pass
        return {
            "function_review": state.get("function_review", ""),
            "security_review": state.get("security_review", ""),
            "ux_review": state.get("ux_review", ""),
            "summary": state.get("summary", ""),
        }
