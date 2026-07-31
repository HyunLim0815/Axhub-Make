"""
AI 运行时模型 — AIRun + AIGenerationTask

- AIRun: 单次 AI 执行记录 (LLM 调用 / Agent 运行)
- AIGenerationTask: 生成任务 (原型/标注/知识库批量生成)
"""

from tortoise import fields

from models.basic_model import BaseModel


class AIRun(BaseModel):
    """AI 执行记录 — 单次推理/Agent 运行的元数据与结果"""

    name = fields.CharField(max_length=255, default="", description="运行名称")
    agent_type = fields.CharField(
        max_length=64,
        default="chat",
        description="Agent 类型: chat | annotate | review | extract | generate",
    )
    status = fields.CharField(
        max_length=32,
        default="pending",
        description="状态: pending | running | completed | failed",
    )
    input_data = fields.JSONField(default=dict, description="输入数据")
    output_data = fields.JSONField(default=dict, description="输出数据")
    error = fields.TextField(default="", description="错误信息")
    duration_ms = fields.IntField(default=0, description="执行耗时 (毫秒)")
    model_used = fields.CharField(max_length=64, default="", description="使用的模型名称")
    project = fields.ForeignKeyField(
        "models.Project", related_name="ai_runs", null=True, description="所属项目"
    )

    class Meta:
        table = "ai_runs"
        ordering = ["-id"]


class AIGenerationTask(BaseModel):
    """AI 生成任务 — prototype | annotation | knowledge"""

    name = fields.CharField(max_length=255, description="任务名称")
    type = fields.CharField(
        max_length=32,
        default="prototype",
        description="任务类型: prototype | annotation | knowledge",
    )
    status = fields.CharField(
        max_length=32,
        default="pending",
        description="状态: pending | running | completed | failed",
    )
    prompt = fields.TextField(default="", description="提示词")
    result = fields.JSONField(default=dict, description="任务结果")
    progress = fields.FloatField(default=0.0, description="进度 0.0 ~ 1.0")
    project = fields.ForeignKeyField(
        "models.Project", related_name="generation_tasks", null=True, description="所属项目"
    )
    prototype = fields.ForeignKeyField(
        "models.Prototype", related_name="generation_tasks", null=True, description="关联原型"
    )
    error = fields.TextField(default="", description="错误信息")

    class Meta:
        table = "ai_generation_tasks"
        ordering = ["-id"]
