"""媒体资源 Schemas"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class MediaUploadResponse(ORMModel):
    """上传响应"""

    id: int
    filename: str
    filepath: str
    size: int
    mime_type: str


class MediaFolderCreate(BaseModel):
    """创建文件夹请求"""

    name: str = Field(..., min_length=1, max_length=255, description="文件夹名称")
    parent: str = Field("", description="父文件夹路径")


class MediaListResponse(ORMModel):
    """媒体文件列表项"""

    id: int
    filename: str
    filepath: str
    mime_type: str
    size: int
    folder: str
    create_time: Optional[datetime] = None
