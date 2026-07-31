"""发布 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    base_url: Optional[str] = None
    access_control: Optional[str] = Field(None, pattern="public|team|invite-only")


class DeployCreate(BaseModel):
    summary: str = ""


class ChannelResponse(ORMModel):
    id: int
    name: str
    type: str
    base_url: str
    access_control: str
    current_version: int
    status: str
    create_time: datetime
    update_time: datetime


class PublishRecordResponse(ORMModel):
    id: int
    channel_id: int
    version: int
    summary: str
    status: str
    create_time: datetime


class DashboardResponse(ORMModel):
    channels: list[ChannelResponse]
    latest_records: list[PublishRecordResponse]
    total_deploys: int
