"""
知识抽取 Agent — 自动从文本中提取知识条目

流程: 关键词预检 → LLM 抽取 → 去重 → 结构化输出
"""

from typing import Any

import structlog

from ai.agents.base import BaseAgent

LOGGER = structlog.get_logger(__name__)

KNOWLEDGE_SYSTEM_PROMPT = """你是一个产品知识抽取助手。从以下对话或文本中提取知识条目。
每项输出 JSON 格式，包含"type"、"title"和"content"字段。

类型说明:
- term: 产品术语或定义
- decision: 设计或产品决策（含原因）
- constraint: 技术或业务约束
- user-feedback: 用户反馈（需具体）
- design-rule: 设计规范或样式规则

如果没有任何可提取的知识，返回空数组 []。"""

# 各类型的触发关键词
TRIGGER_KEYWORDS: dict[str, list[str]] = {
    "term": ["术语", "定义", "简称", "缩写", "指的是", "称为", "叫做"],
    "decision": ["决定", "决策", "选择", "采用", "放弃", "确认", "同意", "结论"],
    "constraint": ["限制", "约束", "必须", "不能", "不支持", "仅支持", "只能"],
    "user-feedback": ["反馈", "建议", "意见", "问题", "体验", "不好", "改进"],
    "design-rule": ["设计规范", "风格", "颜色", "间距", "字体", "对齐", "布局"],
}


class KnowledgeAgent(BaseAgent):
    """知识抽取 Agent"""

    @staticmethod
    def has_trigger_keywords(text: str) -> list[str]:
        """检测文本中的触发关键词"""
        detected = []
        text_lower = text.lower()
        for entry_type, keywords in TRIGGER_KEYWORDS.items():
            if any(kw.lower() in text_lower for kw in keywords):
                detected.append(entry_type)
        return detected

    async def extract(
        self,
        text: str,
        source: str = "",
    ) -> list[dict[str, Any]]:
        """从文本中抽取知识条目

        Args:
            text: 源文本
            source: 来源标识

        Returns:
            知识条目列表
        """
        # 1. 关键词预检
        detected_types = self.has_trigger_keywords(text)
        if not detected_types:
            LOGGER.info("No trigger keywords found, skipping")
            return []

        LOGGER.bind(
            detected_types=detected_types,
            text_length=len(text),
        ).info("Extracting knowledge")

        # 2. LLM 抽取
        result = await self._llm_call(
            KNOWLEDGE_SYSTEM_PROMPT,
            f"从以下文本中抽取知识条目：\n\n{text}\n\n"
            f"来源：{source if source else '未知'}",
        )

        # 3. 解析 JSON 结果
        entries = self._parse_result(result)

        # 4. 标注来源
        for entry in entries:
            if source:
                entry["source"] = source

        LOGGER.bind(extracted=len(entries)).info("Knowledge extracted")
        return entries

    def _parse_result(self, raw: str) -> list[dict[str, Any]]:
        """解析 LLM 返回的 JSON"""
        import json
        import re

        try:
            # 尝试提取 JSON 数组
            json_match = re.search(r"\[[\s\S]*\]", raw)
            if json_match:
                entries = json.loads(json_match.group(0))
                if isinstance(entries, list):
                    return [
                        {
                            "type": e.get("type", "decision"),
                            "title": e.get("title", ""),
                            "content": e.get("content", ""),
                        }
                        for e in entries
                        if e.get("title") and e.get("content")
                    ]
        except (json.JSONDecodeError, TypeError):
            LOGGER.warning("Failed to parse extraction result")
        return []
