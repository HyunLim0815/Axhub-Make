"""云发布 Schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


# ── 云发布配置 ──


class CloudPublishConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=128)
    provider: str = Field("axhub", max_length=32)
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class CloudPublishConfigUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=128)
    provider: str | None = Field(None, max_length=32)
    config: dict[str, Any] | None = None
    enabled: bool | None = None


class CloudPublishConfigResponse(ORMModel):
    id: int
    name: str
    provider: str
    config: dict[str, Any]
    enabled: bool
    create_time: datetime


# ── 发布请求 / 结果 ──


class PublishRequest(BaseModel):
    config_id: int
    summary: str = ""


class PublishResult(BaseModel):
    success: bool
    url: str = ""
    version: int
    message: str


# ── Axhub 连接 ──


class AxhubConnectRequest(BaseModel):
    code: str
    redirect_uri: str = ""
    is_enterprise: bool = False
    enterprise_url: str = ""


class AxhubStatusResponse(ORMModel):
    connected: bool
    user_info: dict[str, Any]
    is_enterprise: bool
