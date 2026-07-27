"""
标注模型 — Annotation + AnnotationVersion

标注是绑定到原型页面或元素上的需求说明。
版本管理追踪每次标注变更。
"""

from tortoise import fields

from models.basic_model import BaseModel


class Annotation(BaseModel):
    """标注 — 绑定到原型元素或页面的需求说明"""

    prototype = fields.ForeignKeyField(
        "models.Prototype", related_name="annotations", description="所属原型"
    )
    title = fields.CharField(max_length=255, default="", description="标注标题")
    annotation_text = fields.TextField(default="", description="短标注文本")
    markdown = fields.TextField(default="", description="Markdown 正文")
    color = fields.CharField(max_length=32, default="#1677FF", description="标注颜色")
    scope = fields.CharField(
        max_length=16, default="element", description="标注粒度: element | page"
    )
    locator = fields.JSONField(default=dict, description="元素定位器 (CSS/fingerprint)")
    page_id = fields.CharField(max_length=255, default="", description="所属页面 ID")
    status = fields.CharField(max_length=32, default="active", description="状态")

    class Meta:
        table = "annotations"
        ordering = ["-id"]


class AnnotationVersion(BaseModel):
    """版本记录 — 每次标注变更的快照"""

    prototype = fields.ForeignKeyField(
        "models.Prototype", related_name="versions", description="所属原型"
    )
    version = fields.IntField(description="版本号（递增）")
    diff = fields.JSONField(default=list, description="变更差异列表")
    summary = fields.CharField(max_length=512, default="", description="变更摘要")
    tags = fields.JSONField(default=list, description="版本标签")
    status = fields.CharField(
        max_length=32, default="draft", description="版本状态: draft | review | released"
    )

    class Meta:
        table = "annotation_versions"
        ordering = ["-version"]
