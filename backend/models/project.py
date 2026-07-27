"""
项目模型 — Project

项目是原型的容器。每个项目包含多个原型和标注。
对应原有 client.json 中的 project 配置。
"""

from tortoise import fields
from models.basic_model import BaseModel


class Project(BaseModel):
    """项目 — 原型和知识库的顶层容器"""

    name = fields.CharField(max_length=255, description="项目名称")
    description = fields.TextField(default="", description="项目描述")

    class Meta:
        table = "projects"
        ordering = ["-id"]
