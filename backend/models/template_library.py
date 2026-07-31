"""模板库与主题库 — Tortoise ORM 模型"""

from tortoise import fields

from models.basic_model import BaseModel


class TemplateLibraryEntry(BaseModel):
    """模板库条目"""

    name = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    category = fields.CharField(max_length=64, default="page")
    content = fields.JSONField(default=dict)
    tags = fields.JSONField(default=list)
    preview_url = fields.CharField(max_length=512, default="")

    class Meta:
        table = "template_library"
        ordering = ["-id"]


class ThemeLibraryEntry(BaseModel):
    """主题库条目"""

    name = fields.CharField(max_length=255)
    description = fields.TextField(default="")
    tokens = fields.JSONField(default=dict)
    colors = fields.JSONField(default=dict)
    typography = fields.JSONField(default=dict)
    preview_url = fields.CharField(max_length=512, default="")

    class Meta:
        table = "theme_library"
        ordering = ["-id"]
