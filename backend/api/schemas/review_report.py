"""审查报告 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class ReviewReportCreate(BaseModel):
    prototype_id: Optional[int] = Field(None, description="所属原型 ID（可空）")
    title: str = Field(..., max_length=255, description="审查标题")
    content: str = Field("", description="审查内容 (Markdown)")
    summary: str = Field("", description="摘要")
    score: int = Field(0, ge=0, le=100, description="评分 0-100")
    reviewers: list[str] = Field(default_factory=list, description="审查人列表")
    categories: list[str] = Field(
        default_factory=list,
        description="审查分类: function/security/ux/accessibility",
    )
    status: str = Field("draft", max_length=32, description="状态: draft/published/archived")


class ReviewReportResponse(ORMModel):
    id: int
    prototype_id: Optional[int] = None
    title: str
    content: str
    summary: str
    score: int
    reviewers: list[str]
    categories: list[str]
    status: str
    source: str
    attachment_path: str
    create_time: datetime
    update_time: datetime


class ReviewReportSubmit(BaseModel):
    prototype_id: Optional[int] = Field(None, description="所属原型 ID（可空）")
    title: str = Field(..., max_length=255, description="审查标题")
    content: str = Field("", description="审查内容 (Markdown)")
    summary: str = Field("", description="摘要")
    score: int = Field(0, ge=0, le=100, description="评分 0-100")
    reviewers: list[str] = Field(default_factory=list, description="审查人列表")
    categories: list[str] = Field(
        default_factory=list,
        description="审查分类: function/security/ux/accessibility",
    )


class AxhubSyncRequest(BaseModel):
    report_id: int = Field(..., description="报告 ID")
    axhub_url: str = Field(..., min_length=1, description="Axhub 地址")
