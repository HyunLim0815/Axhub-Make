"""
模型路由 — 三级选择

根据任务复杂度将请求路由到不同模型：
- simple (40%): gpt-4o-mini — 低成本快速响应
- medium (40%): gpt-4o — 平衡能力与成本
- complex (20%): o3-mini — 强推理/多步分析
"""

import structlog
from config.db import get_settings

LOGGER = structlog.get_logger(__name__)


class ComplexityEstimator:
    """任务复杂度评估"""

    # 简单任务关键词
    SIMPLE_KEYWORDS = [
        "分类", "提取", "摘要", "翻译", "格式化", "标签",
        "classify", "extract", "summarize", "translate", "format",
        "简短", "列举", "list", "simple",
    ]

    # 复杂任务关键词
    COMPLEX_KEYWORDS = [
        "多步", "推理", "分析", "对比", "规划", "策略",
        "reason", "analyze", "compare", "plan", "strategy",
        "架构", "设计", "architecture", "design", "complex",
        "代码生成", "code generation", "debug", "优化",
    ]

    @classmethod
    def estimate(cls, prompt: str, context: dict | None = None) -> str:
        """评估任务复杂度

        Args:
            prompt: 用户提示词
            context: 可选上下文信息

        Returns:
            "simple" | "medium" | "complex"
        """
        prompt_lower = prompt.lower()

        # 检查复杂关键词
        complex_score = sum(1 for kw in cls.COMPLEX_KEYWORDS if kw.lower() in prompt_lower)
        # 检查简单关键词
        simple_score = sum(1 for kw in cls.SIMPLE_KEYWORDS if kw.lower() in prompt_lower)

        # Prompt 长度也是一个因素
        length_score = min(len(prompt) / 1000, 3)  # 超过 1000 字加分

        # 上下文复杂度
        context_score = 0
        if context:
            context_score = min(len(str(context)) / 2000, 2)

        total_score = complex_score * 2 - simple_score + length_score + context_score

        LOGGER.bind(
            complex_score=complex_score,
            simple_score=simple_score,
            length_score=length_score,
            context_score=context_score,
            total_score=total_score,
            result="complex" if total_score > 3 else ("simple" if total_score < 0 else "medium"),
        ).debug("Complexity estimated")

        if total_score > 3:
            return "complex"
        elif total_score < 0:
            return "simple"
        return "medium"


class ModelRouter:
    """模型路由 — 根据复杂度选择模型"""

    @staticmethod
    def route(prompt: str, context: dict | None = None) -> str:
        """路由到合适的模型

        Args:
            prompt: 用户提示词
            context: 可选上下文

        Returns:
            模型名称 (如 gpt-4o)
        """
        settings = get_settings()
        complexity = ComplexityEstimator.estimate(prompt, context)

        model_map = {
            "simple": settings.AI_SIMPLE_MODEL,
            "medium": settings.AI_MODEL,
            "complex": settings.AI_COMPLEX_MODEL,
        }

        selected_model = model_map.get(complexity, settings.AI_MODEL)

        LOGGER.bind(
            complexity=complexity,
            model=selected_model,
            prompt_length=len(prompt),
        ).info("Model routed")

        return selected_model
