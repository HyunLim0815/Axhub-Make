"""HTML 审查与编辑 Schemas"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


# ── 图表 Schemas ──


class DiagramCreate(BaseModel):
    prototype_id: Optional[int] = Field(None, description="所属原型 ID（可空）")
    name: str = Field(..., max_length=255, description="图表名称")
    content: dict[str, Any] = Field(default_factory=dict, description="图表内容")
    type: str = Field("diagram", max_length=32, description="图表类型")


class DiagramResponse(ORMModel):
    id: int
    name: str
    content: dict[str, Any]
    type: str
    create_time: datetime


# ── 文本编辑 Schemas ──


class TextEditCreate(BaseModel):
    prototype_id: Optional[int] = Field(None, description="所属原型 ID（可空）")
    element_selector: str = Field("", max_length=512, description="元素选择器")
    original_text: str = Field("", description="原始文本")
    edited_text: str = Field("", description="编辑后文本")


class TextEditResponse(ORMModel):
    id: int
    element_selector: str
    original_text: str
    edited_text: str
    status: str
    create_time: datetime


# ── 样式修补 Schemas ──


class StyleHackRequest(BaseModel):
    selector: str = Field(..., min_length=1, description="CSS 选择器")
    css: str = Field(..., min_length=1, description="CSS 规则内容")
