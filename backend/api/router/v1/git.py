"""Git 版本管理 API 路由"""

from fastapi import APIRouter, Query

from api.controllers.GitController import GitController
from api.responses.Base import ApiResponse

router = APIRouter(prefix="/v1/git", tags=["git"])


@router.get("/status", response_model=ApiResponse)
async def get_git_status():
    """获取 Git 仓库状态"""
    data = await GitController.status()
    return ApiResponse(data=data)


@router.get("/history", response_model=ApiResponse)
async def get_git_history(max_count: int = Query(20, ge=1, le=200)):
    """获取提交历史"""
    entries = await GitController.log(max_count=max_count)
    return ApiResponse(data=entries)


@router.get("/diff", response_model=ApiResponse)
async def get_git_diff(
    file: str = Query(default=""),
    from_hash: str = Query(default=None),
    to_hash: str = Query(default=None),
):
    """获取文件 diff"""
    content = await GitController.diff(file=file, from_hash=from_hash, to_hash=to_hash)
    return ApiResponse(data=content)


@router.post("/commit", response_model=ApiResponse)
async def post_git_commit(message: str, paths: list[str] = Query(default=[])):
    """提交更改"""
    result = await GitController.commit(message=message, paths=paths or None)
    return ApiResponse(data=result)


@router.post("/restore", response_model=ApiResponse)
async def post_git_restore(file: str, version: str = Query(default=None)):
    """恢复文件"""
    await GitController.restore(file=file, version=version)
    return ApiResponse(message="restored")


@router.post("/workspace/init", response_model=ApiResponse)
async def post_git_workspace_init(path: str = "."):
    """初始化 Git 仓库"""
    result = await GitController.init_workspace(path=path)
    return ApiResponse(data=result)


@router.post("/workspace/remote", response_model=ApiResponse)
async def post_git_workspace_remote(url: str, name: str = "origin"):
    """添加远程仓库"""
    result = await GitController.set_remote(url=url, name=name)
    return ApiResponse(data=result)


@router.post("/workspace/push", response_model=ApiResponse)
async def post_git_workspace_push(remote: str = "origin", branch: str = "main"):
    """推送到远程仓库"""
    result = await GitController.push(remote=remote, branch=branch)
    return ApiResponse(data=result)


@router.post("/workspace/fetch", response_model=ApiResponse)
async def post_git_workspace_fetch():
    """从远程仓库拉取"""
    result = await GitController.fetch()
    return ApiResponse(data=result)


@router.get("/version-file/{path:path}", response_model=ApiResponse)
async def get_git_version_file(path: str, version: str = Query(default="HEAD")):
    """读取指定版本的文件内容"""
    content = await GitController.show_file(path=path, version=version)
    return ApiResponse(data=content)
