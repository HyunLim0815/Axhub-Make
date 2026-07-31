"""HTML 审查与编辑控制器"""
from typing import Any, Optional

import structlog

from models.review_artifact import ReviewDiagram, TextEdit

LOGGER = structlog.get_logger(__name__)


class HtmlReviewController:
    """HTML 审查：图表管理、文本编辑、样式修补"""

    # ── 图表管理 ──
    @staticmethod
    async def create_diagram(data: dict[str, Any]) -> ReviewDiagram:
        d = await ReviewDiagram.create(**data)
        LOGGER.bind(diagram_id=d.id, name=d.name).info("Review diagram created")
        return d

    @staticmethod
    async def get_diagrams(prototype_id: Optional[int] = None, page: int = 1, size: int = 10) -> tuple[list[ReviewDiagram], int]:
        query = ReviewDiagram.filter(delete_time=None)
        if prototype_id:
            query = query.filter(prototype_id=prototype_id)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total

    # ── 文本编辑 ──
    @staticmethod
    async def create_text_edit(data: dict[str, Any]) -> TextEdit:
        e = await TextEdit.create(**data)
        LOGGER.bind(edit_id=e.id, selector=e.element_selector).info("Text edit created")
        return e

    @staticmethod
    async def get_text_edits(prototype_id: Optional[int] = None) -> list[TextEdit]:
        query = TextEdit.filter(delete_time=None)
        if prototype_id:
            query = query.filter(prototype_id=prototype_id)
        return await query.order_by("-id")

    @staticmethod
    async def apply_text_edit(id_: int) -> Optional[TextEdit]:
        edit = await TextEdit.get_by_id(id_)
        if not edit:
            return None
        edit.status = "applied"
        await edit.save()
        return edit

    # ── 样式修补（直接用 CSS 覆盖） ──
    @staticmethod
    def build_style_hack(selector: str, css: str) -> dict[str, str]:
        """生成样式修补 CSS 片段"""
        css_block = f"{selector} {{\n{css}\n}}"
        return {"css": css_block}
