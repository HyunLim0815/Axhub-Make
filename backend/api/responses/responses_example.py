"""
响应示例 — 供 API 文档 / 测试使用
"""

from api.responses.Base import ApiResponse, PageResponse


class ApiResponseExample:
    """API 响应示例"""

    success = ApiResponse(code=200, message="success", data={})
    created = ApiResponse(code=201, message="created", data={"id": 1})
    not_found = ApiResponse(code=404, message="not found")
    server_error = ApiResponse(code=500, message="internal server error")


def paginated_response_example(data: list) -> PageResponse:
    """生成分页响应示例"""
    return PageResponse(
        data=data,
        total=len(data),
        current_page=1,
        last_page=1,
        per_page=10,
    )
