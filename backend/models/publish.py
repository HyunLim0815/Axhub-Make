"""
发布模型 — PublishChannel + PublishRecord

多环境发布管理。
默认通道: development(开发版), review(评审版), production(正式版)
"""

from tortoise import fields

from models.basic_model import BaseModel


class PublishChannel(BaseModel):
    """发布通道 — 目标环境"""

    name = fields.CharField(max_length=128, description="通道名称")
    type = fields.CharField(
        max_length=32, description="通道类型: development | review | production"
    )
    base_url = fields.CharField(max_length=512, default="", description="部署基础 URL")
    access_control = fields.CharField(
        max_length=32, default="team", description="访问控制: public | team | invite-only"
    )
    current_version = fields.IntField(default=0, description="当前发布版本")
    status = fields.CharField(
        max_length=32, default="pending", description="状态: pending | published"
    )

    class Meta:
        table = "publish_channels"
        ordering = ["-id"]


class PublishRecord(BaseModel):
    """发布记录 — 每次部署的详情"""

    channel = fields.ForeignKeyField(
        "models.PublishChannel", related_name="records", description="发布通道"
    )
    version = fields.IntField(description="发布版本号")
    summary = fields.CharField(max_length=512, default="", description="发布说明")
    status = fields.CharField(
        max_length=32, default="published", description="状态: published | failed"
    )
    error = fields.TextField(default="", description="错误信息（如果失败）")

    class Meta:
        table = "publish_records"
        ordering = ["-version"]
