"""项目 API 路由 + 项目内原型嵌套"""

from fastapi import APIRouter, Query

from api.controllers.ProjectController import ProjectController
from api.controllers.PrototypeController import PrototypeController
from api.responses.Base import ApiResponse, PageResponse
from api.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from api.schemas.prototype import PrototypeResponse

router = APIRouter(prefix="/v1/projects", tags=["projects"])


# ── 项目 CRUD ──


@router.get("/{id}", response_model=ApiResponse)
async def get_project(id: int):
    project = await ProjectController.get_by_id(id)
    if not project:
        return ApiResponse(code=404, message="project not found")
    # 统计该项目的原型数
    from models.prototype import Prototype
    count = await Prototype.filter(project_id=id, delete_time=None).count()
    data = ProjectResponse(
        id=project.id, name=project.name, description=project.description or "",
        create_time=project.create_time, update_time=project.update_time,
        prototype_count=count,
    )
    return ApiResponse(data=data.model_dump())


@router.get("/", response_model=ApiResponse)
async def list_projects(page: int = Query(1, ge=1), size: int = Query(10, gt=0, le=200)):
    projects, total = await ProjectController.get_list(page, size)
    # 统计每个项目的原型数
    from models.prototype import Prototype
    result = []
    for p in projects:
        count = await Prototype.filter(project_id=p.id, delete_time=None).count()
        result.append(ProjectResponse(
            id=p.id, name=p.name, description=p.description or "",
            create_time=p.create_time, update_time=p.update_time,
            prototype_count=count,
        ).model_dump())
    data = PageResponse(
        data=result, total=total, current_page=page,
        last_page=-(-total // size), per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_project(body: ProjectCreate):
    project = await ProjectController.create(body.model_dump())
    return ApiResponse(
        code=201, message="created",
        data=ProjectResponse(
            id=project.id, name=project.name, description=project.description or "",
            create_time=project.create_time, update_time=project.update_time,
        ).model_dump(),
    )


@router.put("/{id}", response_model=ApiResponse)
async def update_project(id: int, body: ProjectUpdate):
    project = await ProjectController.update(id, body.model_dump(exclude_none=True))
    if not project:
        return ApiResponse(code=404, message="project not found")
    return ApiResponse(data=ProjectResponse(
        id=project.id, name=project.name, description=project.description or "",
        create_time=project.create_time, update_time=project.update_time,
    ).model_dump())


@router.delete("/{id}", response_model=ApiResponse)
async def delete_project(id: int):
    deleted = await ProjectController.delete(id)
    if not deleted:
        return ApiResponse(code=404, message="project not found")
    return ApiResponse(message="deleted")


# ── 项目内原型 ──


@router.get("/{project_id}/prototypes", response_model=ApiResponse)
async def list_project_prototypes(
    project_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, gt=0, le=200),
):
    prototypes, total = await PrototypeController.get_list_by_project(
        project_id, page, size
    )
    data = PageResponse(
        data=[PrototypeResponse.model_validate(p).model_dump() for p in prototypes],
        total=total, current_page=page,
        last_page=-(-total // size), per_page=size,
    )
    return ApiResponse(data=data.model_dump())


@router.post("/{project_id}/prototypes", response_model=ApiResponse, status_code=201)
async def create_project_prototype(project_id: int, name: str = "新原型", description: str = ""):
    from api.controllers.PrototypeController import PrototypeController
    proto = await PrototypeController.create({
        "project_id": project_id,
        "name": name,
        "description": description,
    })
    return ApiResponse(
        code=201, message="created",
        data=PrototypeResponse.model_validate(proto).model_dump(),
    )
