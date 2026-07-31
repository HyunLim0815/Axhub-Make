"""文档 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="文档标题")
    content: Optional[str] = Field("", description="文档内容")
    project_id: Optional[int] = Field(None, description="关联项目 ID")
    tags: list[str] = Field(default_factory=list, description="标签列表")


class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="文档标题")
    content: Optional[str] = Field(None, description="文档内容")
    project_id: Optional[int] = Field(None, description="关联项目 ID")
    tags: Optional[list[str]] = Field(None, description="标签列表")


class DocumentResponse(ORMModel):
    id: int
    title: str
    content: str
    file_path: str
    mime_type: str
    tags: list[str]
    project_id: Optional[int] = None
    create_time: datetime
    update_time: datetime


class DocumentTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="模板名称")
    description: str = Field("", description="模板描述")
    category: str = Field("general", max_length=64, description="模板分类")
    content: str = Field("", description="模板内容")


class DocumentTemplateResponse(ORMModel):
    id: int
    name: str
    description: str
    category: str
    content: str
    create_time: datetime
    update_time: datetime


class CheckReferencesRequest(BaseModel):
    content: str = Field(..., description="要检查引用关系的文档内容")
