"""媒体资源 API 路由"""

from fastapi import APIRouter, File, Form, Query, UploadFile
from fastapi.responses import Response

from api.controllers.MediaController import MediaController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.media import MediaFolderCreate, MediaListResponse, MediaUploadResponse

router = APIRouter(prefix="/v1/media", tags=["media"])


@router.get("/", response_model=ApiResponse)
async def list_media(
    folder: str = Query("", description="文件夹路径"),
    project_id: int | None = Query(None, description="项目 ID"),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    """获取媒体文件列表"""
    items, total = await MediaController.list(folder, project_id, page, size)
    data = PageResponse(
        data=[MediaListResponse(
            id=m.id,
            filename=m.filename,
            filepath=m.filepath,
            mime_type=m.mime_type,
            size=m.size,
            folder=m.folder,
            create_time=m.create_time,
        ).model_dump() for m in items],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/upload", response_model=ApiResponse, status_code=201)
async def upload_media(
    file: UploadFile = File(..., description="上传文件"),
    folder: str = Form("", description="分类文件夹"),
    project_id: int | None = Form(None, description="所属项目 ID"),
):
    """上传媒体文件"""
    content = await file.read()
    record = await MediaController.upload(
        file_content=content,
        filename=file.filename or "untitled",
        mime_type=file.content_type or "",
        folder=folder,
        project_id=project_id,
    )
    return ApiResponse(
        code=201,
        message="uploaded",
        data=MediaUploadResponse(
            id=record.id,
            filename=record.filename,
            filepath=record.filepath,
            size=record.size,
            mime_type=record.mime_type,
        ).model_dump(),
    )


@router.post("/folder", response_model=ApiResponse, status_code=201)
async def create_folder(body: MediaFolderCreate):
    """创建分类文件夹"""
    result = await MediaController.create_folder(body.name, body.parent)
    return ApiResponse(code=201, message="created", data=result)


@router.delete("/{id}", response_model=ApiResponse)
async def delete_media(id: int):
    """删除媒体文件"""
    deleted = await MediaController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="media file not found")
    return ApiResponse(message="deleted")


@router.get("/file/{path:path}", response_class=Response)
async def get_media_file(path: str):
    """获取媒体文件内容（用于直接展示/下载）"""
    content = await MediaController.get_file(path)
    if content is None:
        return Response(status_code=404)
    return Response(content=content, media_type="application/octet-stream")
