"""审查报告 API 路由"""

from fastapi import APIRouter, File, Form, Query, UploadFile

from api.controllers.ReviewReportController import ReviewReportController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.review_report import (
    AxhubSyncRequest,
    ReviewReportCreate,
    ReviewReportResponse,
    ReviewReportSubmit,
)
from models.review_report import ReviewReport

router = APIRouter(prefix="/v1/review-reports", tags=["review-reports"])


# ── 检查报告是否存在（须在 /{id} 之前注册）──


@router.get("/exists", response_model=ApiResponse)
async def check_report_exists(
    title: str | None = Query(None, description="标题"),
    prototype_id: int | None = Query(None, description="所属原型 ID"),
):
    query = ReviewReport.filter(delete_time=None)
    if title:
        query = query.filter(title=title)
    if prototype_id:
        query = query.filter(prototype_id=prototype_id)
    exists = await query.exists()
    return ApiResponse(data={"exists": exists})


# ── 报告列表 ──


@router.get("/", response_model=ApiResponse)
async def list_reports(
    prototype_id: int | None = Query(None, description="按原型过滤"),
    status: str | None = Query(None, description="按状态过滤"),
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    reports, total = await ReviewReportController.get_list(
        prototype_id=prototype_id, status=status, page=page, size=size
    )
    data = PageResponse(
        data=[ReviewReportResponse.model_validate(r).model_dump() for r in reports],
        total=total,
        current_page=page,
        last_page=-(-total // size),
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


# ── 创建报告 ──


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_report(body: ReviewReportCreate):
    report = await ReviewReportController.create(body.model_dump())
    return ApiResponse(
        code=201,
        message="created",
        data=ReviewReportResponse.model_validate(report).model_dump(),
    )


# ── 提交报告 ──


@router.post("/submit", response_model=ApiResponse, status_code=201)
async def submit_report(body: ReviewReportSubmit):
    report = await ReviewReportController.submit(body.model_dump())
    return ApiResponse(
        code=201,
        message="submitted",
        data=ReviewReportResponse.model_validate(report).model_dump(),
    )


# ── 上传附件 ──


@router.post("/upload", response_model=ApiResponse, status_code=201)
async def upload_report_attachment(
    file: UploadFile = File(..., description="附件文件"),
    report_id: int = Form(..., description="报告 ID"),
):
    content = await file.read()
    report = await ReviewReportController.upload_attachment(
        report_id=report_id,
        file_content=content,
        filename=file.filename or "attachment",
    )
    if not report:
        return ApiResponse(code=404, message="report not found")
    return ApiResponse(
        code=201,
        message="uploaded",
        data=ReviewReportResponse.model_validate(report).model_dump(),
    )


# ── 同步到 Axhub ──


@router.post("/axhub-sync", response_model=ApiResponse)
async def sync_report_to_axhub(body: AxhubSyncRequest):
    result = await ReviewReportController.sync_to_axhub(body.report_id, body.axhub_url)
    if not result.get("success"):
        return ApiResponse(code=404, message=result.get("message", "sync failed"))
    return ApiResponse(data=result)


# ── 报告详情 ──


@router.get("/{id}", response_model=ApiResponse)
async def get_report(id: int):
    report = await ReviewReportController.get_by_id(id)
    if not report:
        return ApiResponse(code=404, message="report not found")
    return ApiResponse(data=ReviewReportResponse.model_validate(report).model_dump())


# ── 更新报告 ──


@router.put("/{id}", response_model=ApiResponse)
async def update_report(id: int, body: ReviewReportCreate):
    report = await ReviewReportController.update(id, body.model_dump(exclude_none=True))
    if not report:
        return ApiResponse(code=404, message="report not found")
    return ApiResponse(data=ReviewReportResponse.model_validate(report).model_dump())


# ── 删除报告 ──


@router.delete("/{id}", response_model=ApiResponse)
async def delete_report(id: int):
    deleted = await ReviewReportController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="report not found")
    return ApiResponse(message="deleted")
