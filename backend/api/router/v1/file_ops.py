"""文件操作 API 路由"""

from fastapi import APIRouter, UploadFile, File, Form

from api.controllers.FileOpsController import FileOpsController
from api.responses.Base import ApiResponse

router = APIRouter(prefix="/v1/files", tags=["files"])


@router.post("/upload", response_model=ApiResponse)
async def upload_file(file: UploadFile = File(...), sub_dir: str = Form("")):
    """上传文件"""
    content = await file.read()
    result = await FileOpsController.upload(content, file.filename or "untitled", sub_dir)
    return ApiResponse(data=result)


@router.post("/copy", response_model=ApiResponse)
async def copy_file(source: str, destination: str):
    """复制文件"""
    ok = await FileOpsController.copy(source, destination)
    if not ok:
        return ApiResponse(code=404, message="source not found")
    return ApiResponse(message="copied")


@router.post("/rename", response_model=ApiResponse)
async def rename_file(old_path: str, new_path: str):
    """重命名文件"""
    ok = await FileOpsController.rename(old_path, new_path)
    if not ok:
        return ApiResponse(code=404, message="source not found")
    return ApiResponse(message="renamed")


@router.post("/delete", response_model=ApiResponse)
async def delete_file(path: str):
    """删除文件"""
    ok = await FileOpsController.delete(path)
    if not ok:
        return ApiResponse(code=404, message="path not found")
    return ApiResponse(message="deleted")


@router.get("/list", response_model=ApiResponse)
async def list_files(sub_dir: str = ""):
    """列出文件列表"""
    items = await FileOpsController.list_dir(sub_dir)
    return ApiResponse(data=items)
