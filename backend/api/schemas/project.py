"""项目 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str
    create_time: datetime
    update_time: datetime
    prototype_count: int = 0
