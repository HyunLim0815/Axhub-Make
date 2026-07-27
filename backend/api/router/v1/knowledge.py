"""知识库 API 路由"""

from fastapi import APIRouter, Query

from api.controllers.KnowledgeController import KnowledgeController
from api.responses.Base import ApiResponse, PageParams, PageResponse
from api.schemas.knowledge import (
    KnowledgeEntryCreate,
    KnowledgeEntryResponse,
    KnowledgeEntryUpdate,
    KnowledgeSearchParams,
)

router = APIRouter(prefix="/v1/knowledge", tags=["knowledge"])


@router.get("/{id}", response_model=ApiResponse)
async def get_entry(id: int):
    entry = await KnowledgeController.get_by_id(id)
    if not entry:
        return ApiResponse(code=404, message="entry not found")
    return ApiResponse(data=KnowledgeEntryResponse.model_validate(entry).model_dump())


@router.get("/", response_model=ApiResponse)
async def list_entries(
    type: str | None = Query(None, alias="type"),
    q: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    if q:
        entries = await KnowledgeController.search(q)
        total = len(entries)
        data = PageResponse(
            data=[KnowledgeEntryResponse.model_validate(e).model_dump() for e in entries],
            total=total,
            current_page=1,
            last_page=1,
            per_page=total or 1,
        )
        return ApiResponse(data=data.model_dump())

    entries, total = await KnowledgeController.get_list(type, page, size)
    data = PageResponse(
        data=[KnowledgeEntryResponse.model_validate(e).model_dump() for e in entries],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_entry(body: KnowledgeEntryCreate):
    entry = await KnowledgeController.create(body.model_dump())
    return ApiResponse(
        code=201,
        message="created",
        data=KnowledgeEntryResponse.model_validate(entry).model_dump(),
    )


@router.put("/{id}", response_model=ApiResponse)
async def update_entry(id: int, body: KnowledgeEntryUpdate):
    entry = await KnowledgeController.update(id, body.model_dump(exclude_none=True))
    if not entry:
        return ApiResponse(code=404, message="entry not found")
    return ApiResponse(data=KnowledgeEntryResponse.model_validate(entry).model_dump())


@router.delete("/{id}", response_model=ApiResponse)
async def delete_entry(id: int):
    deleted = await KnowledgeController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="entry not found")
    return ApiResponse(message="deleted")
