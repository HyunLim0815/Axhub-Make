"""标注 Schemas"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AnnotationCreate(BaseModel):
    prototype_id: int
    title: str = Field("", max_length=255)
    annotation_text: str = ""
    markdown: str = ""
    color: str = "#1677FF"
    scope: str = "element"  # element | page
    locator: dict[str, Any] = {}
    page_id: str = ""


class AnnotationUpdate(BaseModel):
    title: Optional[str] = None
    annotation_text: Optional[str] = None
    markdown: Optional[str] = None
    color: Optional[str] = None
    scope: Optional[str] = None
    locator: Optional[dict[str, Any]] = None
    status: Optional[str] = None


class AnnotationResponse(BaseModel):
    id: int
    prototype_id: int
    title: str
    annotation_text: str
    markdown: str
    color: str
    scope: str
    locator: dict[str, Any]
    page_id: str
    status: str
    create_time: datetime
    update_time: datetime


# ── 版本 Schemas ──


class AnnotationVersionCreate(BaseModel):
    summary: str = Field(..., min_length=1, max_length=512)
    tags: list[str] = []


class AnnotationVersionResponse(BaseModel):
    id: int
    prototype_id: int
    version: int
    diff: list[dict[str, Any]]
    summary: str
    tags: list[str]
    status: str
    create_time: datetime
