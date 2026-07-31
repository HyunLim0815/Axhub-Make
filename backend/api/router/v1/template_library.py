"""模板库与主题库 API 路由"""

from fastapi import APIRouter, Query

from api.controllers.TemplateLibraryController import TemplateLibraryController
from api.controllers.ThemeLibraryController import ThemeLibraryController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.template_library import (
    TemplateCreate,
    TemplateImportRequest,
    TemplateResponse,
    TemplateUpdate,
    ThemeCreate,
    ThemeImportRequest,
    ThemeResponse,
    ThemeUpdate,
)

router = APIRouter(tags=["template-library"])

# ════════════════════════════════════════════════════════
# 模板库
# ════════════════════════════════════════════════════════

_template_router = APIRouter(prefix="/v1/template-library", tags=["template-library"])


@_template_router.get("/{id}", response_model=ApiResponse)
async def get_template(id: int):
    entry = await TemplateLibraryController.get_by_id(id)
    if not entry:
        return ApiResponse(code=404, message="template not found")
    return ApiResponse(data=TemplateResponse.model_validate(entry).model_dump())


@_template_router.get("/", response_model=ApiResponse)
async def list_templates(
    category: str | None = Query(None),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    if q:
        entries = await TemplateLibraryController.search(q)
        total = len(entries)
        data = PageResponse(
            data=[TemplateResponse.model_validate(e).model_dump() for e in entries],
            total=total, current_page=1, last_page=1, per_page=total or 1,
        )
        return ApiResponse(data=data.model_dump())

    entries, total = await TemplateLibraryController.get_list(category, page, size)
    data = PageResponse(
        data=[TemplateResponse.model_validate(e).model_dump() for e in entries],
        total=total, current_page=page,
        last_page=-(-total // size), per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@_template_router.post("/", response_model=ApiResponse, status_code=201)
async def create_template(body: TemplateCreate):
    entry = await TemplateLibraryController.create(body.model_dump())
    return ApiResponse(
        code=201, message="created",
        data=TemplateResponse.model_validate(entry).model_dump(),
    )


@_template_router.put("/{id}", response_model=ApiResponse)
async def update_template(id: int, body: TemplateUpdate):
    entry = await TemplateLibraryController.update(id, body.model_dump(exclude_none=True))
    if not entry:
        return ApiResponse(code=404, message="template not found")
    return ApiResponse(data=TemplateResponse.model_validate(entry).model_dump())


@_template_router.delete("/{id}", response_model=ApiResponse)
async def delete_template(id: int):
    deleted = await TemplateLibraryController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="template not found")
    return ApiResponse(message="deleted")


@_template_router.post("/import", response_model=ApiResponse, status_code=201)
async def import_template(body: TemplateImportRequest):
    entry = await TemplateLibraryController.import_from_url(body.source_url, body.name)
    return ApiResponse(
        code=201, message="imported",
        data=TemplateResponse.model_validate(entry).model_dump(),
    )


router.include_router(_template_router)

# ════════════════════════════════════════════════════════
# 主题库
# ════════════════════════════════════════════════════════

_theme_router = APIRouter(prefix="/v1/theme-library", tags=["theme-library"])


@_theme_router.get("/{id}", response_model=ApiResponse)
async def get_theme(id: int):
    entry = await ThemeLibraryController.get_by_id(id)
    if not entry:
        return ApiResponse(code=404, message="theme not found")
    return ApiResponse(data=ThemeResponse.model_validate(entry).model_dump())


@_theme_router.get("/", response_model=ApiResponse)
async def list_themes(
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    if q:
        entries = await ThemeLibraryController.search(q)
        total = len(entries)
        data = PageResponse(
            data=[ThemeResponse.model_validate(e).model_dump() for e in entries],
            total=total, current_page=1, last_page=1, per_page=total or 1,
        )
        return ApiResponse(data=data.model_dump())

    entries, total = await ThemeLibraryController.get_list(page, size)
    data = PageResponse(
        data=[ThemeResponse.model_validate(e).model_dump() for e in entries],
        total=total, current_page=page,
        last_page=-(-total // size), per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@_theme_router.post("/", response_model=ApiResponse, status_code=201)
async def create_theme(body: ThemeCreate):
    entry = await ThemeLibraryController.create(body.model_dump())
    return ApiResponse(
        code=201, message="created",
        data=ThemeResponse.model_validate(entry).model_dump(),
    )


@_theme_router.put("/{id}", response_model=ApiResponse)
async def update_theme(id: int, body: ThemeUpdate):
    entry = await ThemeLibraryController.update(id, body.model_dump(exclude_none=True))
    if not entry:
        return ApiResponse(code=404, message="theme not found")
    return ApiResponse(data=ThemeResponse.model_validate(entry).model_dump())


@_theme_router.delete("/{id}", response_model=ApiResponse)
async def delete_theme(id: int):
    deleted = await ThemeLibraryController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="theme not found")
    return ApiResponse(message="deleted")


@_theme_router.post("/import", response_model=ApiResponse, status_code=201)
async def import_theme(body: ThemeImportRequest):
    entry = await ThemeLibraryController.import_from_url(body.source_url, body.name)
    return ApiResponse(
        code=201, message="imported",
        data=ThemeResponse.model_validate(entry).model_dump(),
    )


router.include_router(_theme_router)
