"""原型 Schemas"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class PrototypeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field("", max_length=2000)
    page_id: str = Field("", max_length=255)


class PrototypeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    page_id: Optional[str] = Field(None, max_length=255)
    canvas_data: Optional[dict[str, Any]] = None


class PrototypeResponse(ORMModel):
    id: int
    name: str
    description: str
    page_id: str
    canvas_data: dict[str, Any]
    create_time: datetime
    update_time: datetime
