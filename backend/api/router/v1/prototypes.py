"""原型 API 路由"""

from fastapi import APIRouter, Depends, Query

from api.controllers.PrototypeController import PrototypeController
from api.responses.Base import ApiResponse, PageParams, PageResponse
from api.schemas.prototype import PrototypeCreate, PrototypeResponse, PrototypeUpdate

router = APIRouter(prefix="/v1/prototypes", tags=["prototypes"])


@router.get("/{id}", response_model=ApiResponse)
async def get_prototype(id: int):
    prototype = await PrototypeController.get_by_id(id)
    if not prototype:
        return ApiResponse(code=404, message="prototype not found")
    return ApiResponse(data=PrototypeResponse.model_validate(prototype).model_dump())


@router.get("/", response_model=ApiResponse)
async def list_prototypes(page: int = Query(1, ge=1), size: int = Query(10, gt=0, le=200)):
    prototypes, total = await PrototypeController.get_list(page, size)
    data = PageResponse(
        data=[PrototypeResponse.model_validate(p).model_dump() for p in prototypes],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_prototype(body: PrototypeCreate):
    prototype = await PrototypeController.create(body.model_dump())
    return ApiResponse(
        code=201,
        message="created",
        data=PrototypeResponse.model_validate(prototype).model_dump(),
    )


@router.put("/{id}", response_model=ApiResponse)
async def update_prototype(id: int, body: PrototypeUpdate):
    prototype = await PrototypeController.update(id, body.model_dump(exclude_none=True))
    if not prototype:
        return ApiResponse(code=404, message="prototype not found")
    return ApiResponse(data=PrototypeResponse.model_validate(prototype).model_dump())


@router.delete("/{id}", response_model=ApiResponse)
async def delete_prototype(id: int):
    deleted = await PrototypeController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="prototype not found")
    return ApiResponse(message="deleted")
