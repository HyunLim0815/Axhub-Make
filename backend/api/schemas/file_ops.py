"""文件操作 Schemas"""

from typing import Optional

from pydantic import BaseModel, Field

from api.responses.Base import ORMModel


class FileUploadResponse(ORMModel):
    """文件上传响应"""

    filename: str
    path: str
    size: int
    mime_type: str = ""


class FileCopyRequest(BaseModel):
    """文件复制请求"""

    source: str = Field(..., description="源文件路径")
    destination: str = Field(..., description="目标文件路径")


class FileRenameRequest(BaseModel):
    """文件重命名请求"""

    old_path: str
    new_path: str


class FileDeleteRequest(BaseModel):
    """文件删除请求"""

    path: str


class FileListResponse(ORMModel):
    """文件列表响应项"""

    name: str
    path: str
    size: int
    is_dir: bool
    mime_type: str = ""
    modified_time: Optional[str] = None
