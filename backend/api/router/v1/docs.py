"""文档 API 路由"""

from fastapi import APIRouter, File, Form, Query, UploadFile

from api.controllers.DocController import DocController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.document import (
    CheckReferencesRequest,
    DocumentCreate,
    DocumentResponse,
    DocumentTemplateCreate,
    DocumentTemplateResponse,
    DocumentUpdate,
)

router = APIRouter(prefix="/v1/docs", tags=["docs"])


# ── 文档 CRUD ──


@router.get("/", response_model=ApiResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
    project_id: int | None = Query(None, description="按项目筛选"),
    keyword: str | None = Query(None, description="按标题关键词搜索"),
):
    documents, total = await DocController.get_list(
        page=page, size=size, project_id=project_id, keyword=keyword,
    )
    result = [
        DocumentResponse(
            id=doc.id, title=doc.title, content=doc.content or "",
            file_path=doc.file_path or "", mime_type=doc.mime_type or "",
            tags=doc.tags or [],
            project_id=getattr(doc, "project_id", None),
            create_time=doc.create_time, update_time=doc.update_time,
        ).model_dump()
        for doc in documents
    ]
    data = PageResponse(
        data=result, total=total, current_page=page,
        last_page=-(-total // size) if total > 0 else 1,
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_document(body: DocumentCreate):
    document = await DocController.create(body.model_dump(exclude_none=True))
    return ApiResponse(
        code=201, message="created",
        data=DocumentResponse(
            id=document.id, title=document.title, content=document.content or "",
            file_path=document.file_path or "", mime_type=document.mime_type or "",
            tags=document.tags or [],
            project_id=getattr(document, "project_id", None),
            create_time=document.create_time, update_time=document.update_time,
        ).model_dump(),
    )



# ── 模板 CRUD（必须先于 /{id} 注册，避免路径冲突） ──


@router.get("/templates", response_model=ApiResponse)
async def list_templates(
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
    category: str | None = Query(None, description="按分类筛选"),
):
    templates, total = await DocController.get_template_list(
        page=page, size=size, category=category,
    )
    result = [
        DocumentTemplateResponse(
            id=t.id, name=t.name, description=t.description or "",
            category=t.category or "general", content=t.content or "",
            create_time=t.create_time, update_time=t.update_time,
        ).model_dump()
        for t in templates
    ]
    data = PageResponse(
        data=result, total=total, current_page=page,
        last_page=-(-total // size) if total > 0 else 1,
        per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/templates", response_model=ApiResponse, status_code=201)
async def create_template(body: DocumentTemplateCreate):
    template = await DocController.create_template(body.model_dump())
    return ApiResponse(
        code=201, message="created",
        data=DocumentTemplateResponse(
            id=template.id, name=template.name, description=template.description or "",
            category=template.category or "general", content=template.content or "",
            create_time=template.create_time, update_time=template.update_time,
        ).model_dump(),
    )


@router.get("/templates/{id}", response_model=ApiResponse)
async def get_template(id: int):
    template = await DocController.get_template_by_id(id)
    if not template:
        return ApiResponse(code=404, message="template not found")
    return ApiResponse(data=DocumentTemplateResponse(
        id=template.id, name=template.name, description=template.description or "",
        category=template.category or "general", content=template.content or "",
        create_time=template.create_time, update_time=template.update_time,
    ).model_dump())


@router.get("/{id}", response_model=ApiResponse)
async def get_document(id: int):
    document = await DocController.get_by_id(id)
    if not document:
        return ApiResponse(code=404, message="document not found")
    return ApiResponse(data=DocumentResponse(
        id=document.id, title=document.title, content=document.content or "",
        file_path=document.file_path or "", mime_type=document.mime_type or "",
        tags=document.tags or [],
        project_id=getattr(document, "project_id", None),
        create_time=document.create_time, update_time=document.update_time,
    ).model_dump())


@router.put("/{id}", response_model=ApiResponse)
async def update_document(id: int, body: DocumentUpdate):
    document = await DocController.update(id, body.model_dump(exclude_none=True))
    if not document:
        return ApiResponse(code=404, message="document not found")
    return ApiResponse(data=DocumentResponse(
        id=document.id, title=document.title, content=document.content or "",
        file_path=document.file_path or "", mime_type=document.mime_type or "",
        tags=document.tags or [],
        project_id=getattr(document, "project_id", None),
        create_time=document.create_time, update_time=document.update_time,
    ).model_dump())


@router.delete("/{id}", response_model=ApiResponse)
async def delete_document(id: int):
    deleted = await DocController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="document not found")
    return ApiResponse(message="deleted")


# ── 文档上传 ──


@router.post("/upload", response_model=ApiResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(..., description="要上传的文档文件"),
    title: str = Form("", description="文档标题，为空则使用文件名"),
):
    file_bytes = await file.read()
    mime_type = file.content_type or "application/octet-stream"
    document = await DocController.upload_file(
        file_bytes=file_bytes,
        filename=file.filename or "untitled",
        mime_type=mime_type,
        title=title,
    )
    return ApiResponse(
        code=201, message="created",
        data=DocumentResponse(
            id=document.id, title=document.title, content=document.content or "",
            file_path=document.file_path or "", mime_type=document.mime_type or "",
            tags=document.tags or [],
            project_id=getattr(document, "project_id", None),
            create_time=document.create_time, update_time=document.update_time,
        ).model_dump(),
    )


# ── 引用检查 ──


@router.post("/check-references", response_model=ApiResponse)
async def check_references(body: CheckReferencesRequest):
    """扫描文档内容中引用的其他文档 ID

    匹配模式: {id:N}、[doc:N] 或 #doc:N
    返回引用到的文档信息（是否存在、标题等）。
    """
    references = await DocController.check_references(body.content)
    return ApiResponse(data={"references": references})
