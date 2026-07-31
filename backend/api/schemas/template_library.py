"""模板库与主题库 Schemas"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


# ── 模板 ──


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)
    category: str = Field("page", max_length=64)
    content: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    category: str | None = Field(None, max_length=64)
    content: dict[str, Any] | None = None
    tags: list[str] | None = None


class TemplateResponse(ORMModel):
    id: int
    name: str
    description: str
    category: str
    content: dict[str, Any]
    tags: list[str]
    preview_url: str = ""
    create_time: datetime
    update_time: datetime


# ── 主题 ──


class ThemeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)
    tokens: dict[str, Any] = Field(default_factory=dict)
    colors: dict[str, Any] = Field(default_factory=dict)
    typography: dict[str, Any] = Field(default_factory=dict)


class ThemeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    tokens: dict[str, Any] | None = None
    colors: dict[str, Any] | None = None
    typography: dict[str, Any] | None = None


class ThemeResponse(ORMModel):
    id: int
    name: str
    description: str
    tokens: dict[str, Any]
    colors: dict[str, Any]
    typography: dict[str, Any]
    preview_url: str = ""
    create_time: datetime
    update_time: datetime


# ── 导入 ──


class TemplateImportRequest(BaseModel):
    source_url: str = Field(..., max_length=2048)
    name: str = Field(..., min_length=1, max_length=255)


class ThemeImportRequest(BaseModel):
    source_url: str = Field(..., max_length=2048)
    name: str = Field(..., min_length=1, max_length=255)
