"""
HTML 审查与编辑模型 — ReviewDiagram + TextEdit

图表管理: 保存 HTML 审查过程中的图表快照（如页面结构图、标注图）。
文本编辑: 记录原型元素文本的编辑草稿与应用状态。
"""

from tortoise import fields

from models.basic_model import BaseModel


class ReviewDiagram(BaseModel):
    """审查图表 — 绑定到原型（可空）或独立存在的图表快照"""

    prototype = fields.ForeignKeyField(
        "models.Prototype",
        related_name="review_diagrams",
        null=True,
        description="所属原型（可空）",
    )
    name = fields.CharField(max_length=255, description="图表名称")
    content = fields.JSONField(default=dict, description="图表内容")
    type = fields.CharField(max_length=32, default="diagram", description="图表类型")

    class Meta:
        table = "review_diagrams"
        ordering = ["-id"]


class TextEdit(BaseModel):
    """文本编辑 — 原型元素文本编辑记录"""

    prototype = fields.ForeignKeyField(
        "models.Prototype",
        related_name="text_edits",
        null=True,
        description="所属原型（可空）",
    )
    element_selector = fields.CharField(
        max_length=512, default="", description="元素选择器 (CSS)"
    )
    original_text = fields.TextField(default="", description="原始文本")
    edited_text = fields.TextField(default="", description="编辑后文本")
    status = fields.CharField(
        max_length=32, default="draft", description="状态: draft | applied"
    )

    class Meta:
        table = "text_edits"
        ordering = ["-id"]
