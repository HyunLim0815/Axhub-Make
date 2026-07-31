"""AI 运行时与任务管理 API 路由

与 ai.py (SSE/Agent 接口) 共用 /v1/ai 前缀，但端点互不冲突。
"""
from fastapi import APIRouter, Query

from api.controllers.AIRuntimeController import AIRuntimeController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.ai_runtime import (
    AIRunCreate,
    AIRunResponse,
    AIGenerationTaskCreate,
    AIGenerationTaskResponse,
)
from models.project import Project
from models.prototype import Prototype

router = APIRouter(prefix="/v1/ai", tags=["ai-runtime"])


# ── AI Run ──


@router.post("/runs", response_model=ApiResponse, status_code=201)
async def create_run(body: AIRunCreate):
    """创建 AI Run"""
    data = body.model_dump(exclude_none=True)
    project_id = data.get("project_id")
    if project_id and not await Project.get_by_id(project_id):
        return ApiResponse(code=404, message="project not found")
    run = await AIRuntimeController.create_run(data)
    return ApiResponse(
        code=201,
        message="created",
        data=AIRunResponse.model_validate(run).model_dump(),
    )


@router.get("/runs", response_model=ApiResponse)
async def list_runs(
    project_id: int | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    """AI Run 列表（支持按项目/状态过滤 + 分页）"""
    runs, total = await AIRuntimeController.get_runs(project_id, status, page, size)
    data = PageResponse(
        data=[AIRunResponse.model_validate(r).model_dump() for r in runs],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.get("/runs/{id}", response_model=ApiResponse)
async def get_run(id: int):
    """AI Run 详情"""
    run = await AIRuntimeController.get_run(id)
    if not run:
        return ApiResponse(code=404, message="run not found")
    return ApiResponse(data=AIRunResponse.model_validate(run).model_dump())


@router.post("/runs/{id}/execute", response_model=ApiResponse)
async def execute_run(id: int):
    """执行 AI Run"""
    run = await AIRuntimeController.execute_run(id)
    if not run:
        return ApiResponse(code=404, message="run not found")
    return ApiResponse(data=AIRunResponse.model_validate(run).model_dump())


# ── 历史产物 ──


@router.get("/artifact-history/assets", response_model=ApiResponse)
async def get_artifact_history(
    project_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """历史产物 — 已完成 (completed) 的 AI Run 记录"""
    runs = await AIRuntimeController.get_artifact_history(project_id, limit)
    data = [AIRunResponse.model_validate(r).model_dump() for r in runs]
    return ApiResponse(data=data)


# ── 生成任务 ──


@router.post("/generation-tasks", response_model=ApiResponse, status_code=201)
async def create_generation_task(body: AIGenerationTaskCreate):
    """创建 AI 生成任务"""
    data = body.model_dump(exclude_none=True)
    project_id = data.get("project_id")
    if project_id and not await Project.get_by_id(project_id):
        return ApiResponse(code=404, message="project not found")
    prototype_id = data.get("prototype_id")
    if prototype_id and not await Prototype.get_by_id(prototype_id):
        return ApiResponse(code=404, message="prototype not found")
    task = await AIRuntimeController.create_task(data)
    return ApiResponse(
        code=201,
        message="created",
        data=AIGenerationTaskResponse.model_validate(task).model_dump(),
    )


@router.get("/generation-tasks", response_model=ApiResponse)
async def list_generation_tasks(
    project_id: int | None = Query(None),
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    """生成任务列表（支持按项目/状态过滤 + 分页）"""
    tasks, total = await AIRuntimeController.get_tasks(project_id, status, page, size)
    data = PageResponse(
        data=[AIGenerationTaskResponse.model_validate(t).model_dump() for t in tasks],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())
