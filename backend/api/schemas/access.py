"""访问控制 Schemas"""

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class PasswordSetRequest(BaseModel):
    """设置访问密码请求"""

    password: str = Field(..., min_length=4, description="新密码")


class LoginRequest(BaseModel):
    """登录请求"""

    password: str = Field(..., description="密码")


class ShareTokenRequest(BaseModel):
    """创建共享令牌请求"""

    name: str = Field("", max_length=128, description="令牌名称")
    expires_in_hours: int = Field(24, gt=0, le=8760, description="有效时长(小时)")


class TokenValidateRequest(BaseModel):
    """验证令牌请求"""

    token: str = Field(..., min_length=1, description="令牌值")


class AccessStatusResponse(ORMModel):
    """访问状态响应"""

    password_set: bool = Field(description="是否已设置密码")
    share_tokens_count: int = Field(description="有效共享令牌数量")
    login_required: bool = Field(description="是否需要登录")
