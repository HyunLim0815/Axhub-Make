"""
知识库模型 — KnowledgeEntry

产品知识条目，支持 5 种类型：
- term: 术语定义
- decision: 设计决策
- constraint: 约束条件
- user-feedback: 用户反馈
- design-rule: 设计规则
"""

from tortoise import fields

from models.basic_model import BaseModel


class KnowledgeEntry(BaseModel):
    """知识条目 — 产品知识库的基本单元"""

    type = fields.CharField(
        max_length=32,
        description="条目类型: term | decision | constraint | user-feedback | design-rule",
    )
    title = fields.CharField(max_length=255, description="条目标题")
    content = fields.TextField(description="条目内容 (Markdown)")
    tags = fields.JSONField(default=list, description="标签列表")
    source = fields.CharField(max_length=512, default="", description="来源")
    scope = fields.CharField(
        max_length=16, default="project",
        description="范围: project(项目知识库) | team(团队知识库)",
    )
    project = fields.ForeignKeyField(
        "models.Project", related_name="knowledge_entries",
        null=True, default=None, description="所属项目(team 范围时为空)",
    )

    class Meta:
        table = "knowledge_entries"
        ordering = ["-id"]
