"""
云发布模型 — CloudPublishConfig + AxhubConnection

云发布配置管理，支持 axhub / figma / custom 提供商。
Axhub 连接管理，OAuth 令牌 + 企业版支持。
"""

from tortoise import fields

from models.basic_model import BaseModel


class CloudPublishConfig(BaseModel):
    """云发布配置 — 目标提供商与连接参数"""

    name = fields.CharField(max_length=128, description="配置名称")
    provider = fields.CharField(
        max_length=32, default="axhub", description="提供商: axhub | figma | custom"
    )
    config = fields.JSONField(default=dict, description="提供商配置（JSON）")
    enabled = fields.BooleanField(default=True, description="是否启用")

    class Meta:
        table = "cloud_publish_configs"
        ordering = ["-id"]


class AxhubConnection(BaseModel):
    """Axhub 连接 — OAuth 令牌与账户信息"""

    name = fields.CharField(max_length=128, default="", description="连接名称")
    access_token = fields.TextField(default="", description="OAuth 访问令牌")
    refresh_token = fields.TextField(default="", description="OAuth 刷新令牌")
    expires_at = fields.DatetimeField(null=True, description="令牌过期时间")
    user_info = fields.JSONField(default=dict, description="用户信息")
    is_enterprise = fields.BooleanField(default=False, description="是否企业版")
    enterprise_url = fields.CharField(max_length=512, default="", description="企业版 URL")
    is_active = fields.BooleanField(default=True, description="是否活跃")

    class Meta:
        table = "axhub_connections"
        ordering = ["-id"]
