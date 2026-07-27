"""
AI Context Bundle — 结构化 AI 交付包

生成供下游 AI (Cursor/Claude Code/Trae) 消费的上下文数据。
"""

from typing import Any

import structlog

from models.annotation import Annotation
from models.knowledge import KnowledgeEntry
from models.prototype import Prototype

LOGGER = structlog.get_logger(__name__)


class ContextBundle:
    """AI 上下文包 — 项目交付的结构化摘要"""

    @staticmethod
    async def build(
        prototype_id: int | None = None,
    ) -> dict[str, Any]:
        """构建完整的 Context Bundle

        Args:
            prototype_id: 可选，指定原型的上下文

        Returns:
            结构化上下文 JSON
        """
        bundle: dict[str, Any] = {
            "schema_version": 1,
            "project": {},
            "pages": [],
            "annotations": [],
            "design_tokens": {},
            "version_info": {},
        }

        # 原型信息
        if prototype_id:
            prototype = await Prototype.get_by_id(prototype_id)
            if prototype:
                bundle["project"] = {
                    "id": prototype.id,
                    "name": prototype.name,
                    "description": prototype.description,
                }

                # 标注摘要
                annotations = await Annotation.filter(
                    prototype_id=prototype_id, delete_time=None
                ).all()
                bundle["annotations"] = [
                    {
                        "id": a.id,
                        "title": a.title,
                        "summary": a.annotation_text or a.markdown[:200] if a.markdown else "",
                        "color": a.color,
                        "scope": a.scope,
                        "page_id": a.page_id,
                    }
                    for a in annotations
                ]

        # 知识库上下文
        entries = await KnowledgeEntry.filter(delete_time=None).all()
        if entries:
            bundle["knowledge"] = {
                "terms": [e.title for e in entries if e.type == "term"],
                "decisions": [e.title for e in entries if e.type == "decision"],
                "constraints": [e.title for e in entries if e.type == "constraint"],
            }

        LOGGER.bind(
            has_prototype=prototype_id is not None,
            annotation_count=len(bundle.get("annotations", [])),
        ).info("Context bundle built")

        return bundle


class PromptPack:
    """Prompt 包 — 面向不同角色的 Prompt 模板"""

    ROLE_TEMPLATES = {
        "engineering": (
            "你是一个前端开发工程师。请根据以下产品需求实现页面。\n\n"
            "## 项目上下文\n{context}\n\n"
            "## 标注说明\n{annotations}\n\n"
            "请严格按照标注说明实现，确保所有状态和边界情况都覆盖。"
        ),
        "testing": (
            "你是一个测试工程师。请根据以下产品需求和标注编写测试用例。\n\n"
            "## 项目上下文\n{context}\n\n"
            "## 标注说明\n{annotations}\n\n"
            "请覆盖正常流程、异常流程和边界情况。"
        ),
        "review": (
            "你是一个产品评审专家。请审查以下原型是否满足需求。\n\n"
            "## 项目上下文\n{context}\n\n"
            "## 标注说明\n{annotations}\n\n"
            "请从功能完整性、用户体验和一致性角度给出评审意见。"
        ),
    }

    @staticmethod
    async def generate(
        role: str,
        prototype_id: int | None = None,
    ) -> str:
        """生成角色特定的 Prompt

        Args:
            role: 角色 (engineering | testing | review)
            prototype_id: 原型 ID

        Returns:
            格式化的 Prompt 文本
        """
        template = PromptPack.ROLE_TEMPLATES.get(role)
        if not template:
            raise ValueError(f"Unknown role: {role}")

        bundle = await ContextBundle.build(prototype_id)

        context_lines = []
        if bundle.get("project"):
            p = bundle["project"]
            context_lines.append(f"- 项目: {p.get('name', '')}")
            context_lines.append(f"- 描述: {p.get('description', '')}")

        if bundle.get("knowledge"):
            k = bundle["knowledge"]
            if k.get("terms"):
                context_lines.append(f"- 术语: {', '.join(k['terms'][:10])}")
            if k.get("constraints"):
                context_lines.append(f"- 约束: {', '.join(k['constraints'][:5])}")

        annotations_lines = []
        for a in bundle.get("annotations", []):
            annotations_lines.append(
                f"- [{a.get('color', '')}] {a.get('title', '')}: {a.get('summary', '')[:100]}"
            )

        prompt = template.format(
            context="\n".join(context_lines) if context_lines else "（无）",
            annotations="\n".join(annotations_lines) if annotations_lines else "（无）",
        )

        LOGGER.bind(role=role, prompt_length=len(prompt)).info("Prompt pack generated")
        return prompt
