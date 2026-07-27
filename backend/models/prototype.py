"""
原型模型 — Prototype

对应原有 client.json 中的原型配置，
存储 Excalidraw 画布数据和页面结构。
"""

from tortoise import fields

from models.basic_model import BaseModel


class Prototype(BaseModel):
    """原型 — 项目的核心实体"""

    name = fields.CharField(max_length=255, description="原型名称")
    description = fields.TextField(default="", description="原型描述")
    page_id = fields.CharField(max_length=255, default="", description="当前页面 ID")
    canvas_data = fields.JSONField(default=dict, description="Excalidraw 画布数据")

    class Meta:
        table = "prototypes"
        ordering = ["-id"]
