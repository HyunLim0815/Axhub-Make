"""AI 运行时 Schemas — Run + GenerationTask 请求/响应"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


# ── AI Run ──


class AIRunCreate(BaseModel):
    """创建 AI Run 请求"""

    name: str = Field("", max_length=255)
    agent_type: str = Field("chat", max_length=64)  # chat | annotate | review | extract | generate
    input_data: dict = Field(default_factory=dict)
    project_id: Optional[int] = None


class AIRunResponse(ORMModel):
    """AI Run 响应"""

    id: int
    name: str
    agent_type: str
    status: str
    input_data: dict
    output_data: dict
    error: str
    duration_ms: int
    model_used: str
    create_time: datetime
    update_time: datetime


# ── 生成任务 ──


class AIGenerationTaskCreate(BaseModel):
    """创建生成任务请求"""

    name: str = Field(..., max_length=255)
    type: str = Field("prototype", max_length=32)  # prototype | annotation | knowledge
    prompt: str = Field("")
    project_id: Optional[int] = None
    prototype_id: Optional[int] = None


class AIGenerationTaskResponse(ORMModel):
    """生成任务响应"""

    id: int
    name: str
    type: str
    status: str
    prompt: str
    result: dict
    progress: float
    error: str
    create_time: datetime
