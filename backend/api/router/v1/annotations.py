"""标注 API 路由"""

from fastapi import APIRouter, Query

from api.controllers.AnnotationController import (
    AnnotationController,
    AnnotationVersionController,
)
from api.responses.Base import ApiResponse, PageParams, PageResponse
from api.schemas.annotation import (
    AnnotationCreate,
    AnnotationResponse,
    AnnotationUpdate,
    AnnotationVersionCreate,
    AnnotationVersionResponse,
)

router = APIRouter(prefix="/v1/annotations", tags=["annotations"])


# ── 标注 CRUD ──


@router.get("/{id}", response_model=ApiResponse)
async def get_annotation(id: int):
    annotation = await AnnotationController.get_by_id(id)
    if not annotation:
        return ApiResponse(code=404, message="annotation not found")
    return ApiResponse(data=AnnotationResponse.model_validate(annotation).model_dump())


@router.get("/", response_model=ApiResponse)
async def list_annotations(
    prototype_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    annotations, total = await AnnotationController.get_list(prototype_id, page, size)
    data = PageResponse(
        data=[AnnotationResponse.model_validate(a).model_dump() for a in annotations],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_annotation(body: AnnotationCreate):
    annotation = await AnnotationController.create(body.model_dump())
    return ApiResponse(
        code=201,
        message="created",
        data=AnnotationResponse.model_validate(annotation).model_dump(),
    )


@router.put("/{id}", response_model=ApiResponse)
async def update_annotation(id: int, body: AnnotationUpdate):
    annotation = await AnnotationController.update(id, body.model_dump(exclude_none=True))
    if not annotation:
        return ApiResponse(code=404, message="annotation not found")
    return ApiResponse(data=AnnotationResponse.model_validate(annotation).model_dump())


@router.delete("/{id}", response_model=ApiResponse)
async def delete_annotation(id: int):
    deleted = await AnnotationController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="annotation not found")
    return ApiResponse(message="deleted")


# ── 版本管理 ──


@router.get("/versions/{prototype_id}", response_model=ApiResponse)
async def list_versions(
    prototype_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    versions, total = await AnnotationVersionController.get_versions(prototype_id, page, size)
    data = PageResponse(
        data=[AnnotationVersionResponse.model_validate(v).model_dump() for v in versions],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/versions/{prototype_id}", response_model=ApiResponse, status_code=201)
async def create_version(prototype_id: int, body: AnnotationVersionCreate):
    version = await AnnotationVersionController.create_version(
        prototype_id, body.summary, body.tags
    )
    return ApiResponse(
        code=201,
        message="created",
        data=AnnotationVersionResponse.model_validate(version).model_dump(),
    )


@router.post("/versions/{prototype_id}/rollback/{target_version}", response_model=ApiResponse)
async def rollback_version(prototype_id: int, target_version: int):
    version = await AnnotationVersionController.rollback(prototype_id, target_version)
    if not version:
        return ApiResponse(code=404, message="target version not found")
    return ApiResponse(
        data=AnnotationVersionResponse.model_validate(version).model_dump(),
    )
