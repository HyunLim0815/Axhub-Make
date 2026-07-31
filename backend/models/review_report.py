"""
审查报告模型 — ReviewReport

记录原型的设计审查结果，支持草稿/发布/归档状态，
可手动、AI 生成或从 Axhub 平台同步。
"""

from tortoise import fields

from models.basic_model import BaseModel


class ReviewReport(BaseModel):
    """审查报告 — 绑定到原型（可空）"""

    prototype = fields.ForeignKeyField(
        "models.Prototype",
        related_name="review_reports",
        null=True,
        description="所属原型（可空）",
    )
    title = fields.CharField(max_length=255, description="审查标题")
    content = fields.TextField(default="", description="审查内容 (Markdown)")
    summary = fields.TextField(default="", description="摘要")
    score = fields.IntField(default=0, description="评分 0-100")
    reviewers = fields.JSONField(default=list, description="审查人列表")
    categories = fields.JSONField(
        default=list,
        description="审查分类: function/security/ux/accessibility",
    )
    status = fields.CharField(
        max_length=32, default="draft", description="状态: draft/published/archived"
    )
    source = fields.CharField(
        max_length=32, default="manual", description="来源: manual/ai/axhub"
    )
    attachment_path = fields.CharField(max_length=512, default="", description="附件路径")

    class Meta:
        table = "review_reports"
        ordering = ["-id"]
