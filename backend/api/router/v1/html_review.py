"""HTML 审查与编辑 API 路由"""

from fastapi import APIRouter, Query

from api.controllers.HtmlReviewController import HtmlReviewController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.review import (
    DiagramCreate,
    DiagramResponse,
    StyleHackRequest,
    TextEditCreate,
    TextEditResponse,
)

router = APIRouter(prefix="/v1/html-review", tags=["html-review"])


# ── 图表管理 ──


@router.get("/diagrams", response_model=ApiResponse)
async def list_diagrams(
    prototype_id: int | None = Query(None, description="按原型过滤"),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    diagrams, total = await HtmlReviewController.get_diagrams(prototype_id, page, size)
    data = PageResponse(
        data=[DiagramResponse.model_validate(d).model_dump() for d in diagrams],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/diagrams", response_model=ApiResponse, status_code=201)
async def create_diagram(body: DiagramCreate):
    diagram = await HtmlReviewController.create_diagram(body.model_dump(exclude_none=True))
    return ApiResponse(
        code=201,
        message="created",
        data=DiagramResponse.model_validate(diagram).model_dump(),
    )


@router.post("/diagram-drafts", response_model=ApiResponse, status_code=201)
async def save_diagram_draft(body: DiagramCreate):
    """保存图表草稿（type 默认为 diagram，可显式指定）"""
    diagram = await HtmlReviewController.create_diagram(body.model_dump(exclude_none=True))
    return ApiResponse(
        code=201,
        message="draft saved",
        data=DiagramResponse.model_validate(diagram).model_dump(),
    )


# ── 文本编辑 ──


@router.get("/text-edits", response_model=ApiResponse)
async def list_text_edits(
    prototype_id: int | None = Query(None, description="按原型过滤"),
):
    edits = await HtmlReviewController.get_text_edits(prototype_id)
    return ApiResponse(
        data=[TextEditResponse.model_validate(e).model_dump() for e in edits],
    )


@router.post("/text-edits", response_model=ApiResponse, status_code=201)
async def create_text_edit(body: TextEditCreate):
    edit = await HtmlReviewController.create_text_edit(body.model_dump(exclude_none=True))
    return ApiResponse(
        code=201,
        message="created",
        data=TextEditResponse.model_validate(edit).model_dump(),
    )


@router.post("/text-edits/{id}/apply", response_model=ApiResponse)
async def apply_text_edit(id: int):
    edit = await HtmlReviewController.apply_text_edit(id)
    if not edit:
        return ApiResponse(code=404, message="text edit not found")
    return ApiResponse(data=TextEditResponse.model_validate(edit).model_dump())


# ── 样式修补 ──


@router.post("/style-hack", response_model=ApiResponse)
async def build_style_hack(body: StyleHackRequest):
    result = HtmlReviewController.build_style_hack(body.selector, body.css)
    return ApiResponse(data=result)
