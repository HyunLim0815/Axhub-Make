"""知识库 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel

# 知识条目类型枚举
ENTRY_TYPES = ["term", "decision", "constraint", "user-feedback", "design-rule"]


class KnowledgeEntryCreate(BaseModel):
    type: str = Field(..., pattern="|".join(ENTRY_TYPES))
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    tags: list[str] = []
    source: str = ""
    scope: str = Field("project", pattern="^(project|team)$")
    project_id: Optional[int] = None


class KnowledgeEntryUpdate(BaseModel):
    type: Optional[str] = Field(None, pattern="|".join(ENTRY_TYPES))
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[list[str]] = None
    source: Optional[str] = None
    scope: Optional[str] = Field(None, pattern="^(project|team)$")


class KnowledgeEntryResponse(ORMModel):
    id: int
    type: str
    title: str
    content: str
    tags: list[str]
    source: str
    scope: str = "project"
    project_id: Optional[int] = None
    create_time: datetime
    update_time: datetime


class KnowledgeSearchParams(BaseModel):
    q: str = Field("", max_length=255)
    type: Optional[str] = Field(None, pattern="|".join(ENTRY_TYPES))
