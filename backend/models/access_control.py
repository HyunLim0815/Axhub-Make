"""
访问控制模型 — AccessToken & AccessLog

AccessToken: 共享访问令牌，用于分享链接/API 调用
AccessLog: 访问日志，记录登录、分享、API 调用行为
"""

from tortoise import fields

from models.basic_model import BaseModel


class AccessToken(BaseModel):
    """访问令牌 — 分享或 API 调用凭证"""

    token = fields.CharField(max_length=255, unique=True, description="令牌值")
    name = fields.CharField(max_length=128, default="", description="令牌名称")
    scope = fields.CharField(max_length=32, default="share", description="作用域: share | api")
    expires_at = fields.DatetimeField(null=True, description="过期时间")
    created_by = fields.CharField(max_length=128, default="", description="创建者")
    is_active = fields.BooleanField(default=True, description="是否有效")

    class Meta:
        table = "access_tokens"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"<AccessToken {self.id}: {self.name or self.token[:8]}...>"


class AccessLog(BaseModel):
    """访问日志 — 登录、分享、API 调用记录"""

    ip_address = fields.CharField(max_length=64, description="来源 IP")
    action = fields.CharField(max_length=64, description="动作: login | share | api_call")
    success = fields.BooleanField(default=True, description="是否成功")
    detail = fields.TextField(default="", description="详情")

    class Meta:
        table = "access_logs"
        ordering = ["-id"]

    def __str__(self) -> str:
        return f"<AccessLog {self.id}: {self.action} {self.ip_address}>"
