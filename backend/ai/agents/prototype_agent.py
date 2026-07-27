"""
原型生成 Agent — LangGraph 工作流

流程: 需求分析 → 布局规划 → 组件生成 → 审查
"""

from typing import Any, AsyncIterator, TypedDict

import structlog
from langgraph.graph import END, StateGraph

from ai.agents.base import BaseAgent
from ai.llm import LLMService

LOGGER = structlog.get_logger(__name__)

PROTOTYPE_SYSTEM_PROMPT = """你是一个专业的原型设计师。根据用户需求生成页面结构描述。
输出格式为 JSON，包含页面布局、组件列表和交互说明。
不要生成代码，只需要结构和说明。"""


class PrototypeState(TypedDict):
    """原型生成状态"""
    requirement: str
    analysis: str
    layout: str
    components: list[dict[str, Any]]
    review: str
    result: str
    iteration: int


class PrototypeAgent(BaseAgent):
    """原型生成 Agent"""

    MAX_ITERATIONS = 3

    def __init__(self, llm: LLMService | None = None) -> None:
        super().__init__(llm)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(PrototypeState)
        builder.add_node("analyze", self._analyze)
        builder.add_node("plan_layout", self._plan_layout)
        builder.add_node("generate", self._generate)
        builder.add_node("review_design", self._review_design)
        builder.set_entry_point("analyze")
        builder.add_edge("analyze", "plan_layout")
        builder.add_edge("plan_layout", "generate")
        builder.add_edge("generate", "review_design")
        builder.add_conditional_edges(
            "review_design",
            self._decide_next,
            {"accept": END, "retry": "plan_layout"},
        )
        return builder.compile()

    async def _analyze(self, state: PrototypeState) -> dict:
        LOGGER.bind(requirement=state["requirement"][:50]).info("Analyzing requirement")
        analysis = await self._llm_call(
            PROTOTYPE_SYSTEM_PROMPT,
            f"分析以下需求，提取关键页面、功能和用户流程：\n{state['requirement']}",
        )
        return {"analysis": analysis, "iteration": 0}

    async def _plan_layout(self, state: PrototypeState) -> dict:
        LOGGER.info("Planning layout")
        layout = await self._llm_call(
            PROTOTYPE_SYSTEM_PROMPT,
            f"基于分析结果规划页面布局：\n{state['analysis']}",
        )
        return {"layout": layout}

    async def _generate(self, state: PrototypeState) -> dict:
        LOGGER.info("Generating components")
        components = await self._llm_call(
            PROTOTYPE_SYSTEM_PROMPT,
            f"基于布局规划生成组件列表：\n{state['layout']}",
        )
        return {"components": [{"name": "generated", "description": components}]}

    async def _review_design(self, state: PrototypeState) -> dict:
        LOGGER.bind(iteration=state["iteration"]).info("Reviewing design")
        review = await self._llm_call(
            "你是一个设计评审专家。检查以下原型设计是否满足用户需求，给出改进建议。",
            f"需求：{state['requirement']}\n\n设计：{state['layout']}\n\n组件：{state['components']}",
        )
        return {"review": review}

    def _decide_next(self, state: PrototypeState) -> str:
        iteration = state.get("iteration", 0) + 1
        if iteration >= self.MAX_ITERATIONS:
            return "accept"
        return "retry"

    async def run(self, requirement: str) -> AsyncIterator[str]:
        """执行原型生成"""
        LOGGER.bind(requirement=requirement[:50]).info("PrototypeAgent started")

        state: PrototypeState = {
            "requirement": requirement,
            "analysis": "",
            "layout": "",
            "components": [],
            "review": "",
            "result": "",
            "iteration": 0,
        }

        async for step in self.graph.astream(state):
            yield str(step)
