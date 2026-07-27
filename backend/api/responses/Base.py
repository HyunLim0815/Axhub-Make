"""
统一响应模型

遵循 fastapi-guider 规范:
- ApiResponse: 统一 JSON 响应
- PageResponse: 分页响应 (Generic)
- PageParams: 分页请求参数
"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel):
    """统一 API 响应"""

    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Optional[dict | list] = Field(None, description="响应数据")


class PageParams(BaseModel):
    """分页请求参数"""

    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, gt=0, le=200, description="每页条数")


class PageResponse(BaseModel, Generic[T]):
    """分页响应"""

    data: list[T] = Field(description="数据列表")
    total: int = Field(description="总条数")
    current_page: int = Field(description="当前页码")
    last_page: int = Field(description="最后一页")
    per_page: int = Field(description="每页条数")
