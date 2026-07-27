"""项目控制器 — 业务逻辑"""

from typing import Any

import structlog

from models.project import Project

LOGGER = structlog.get_logger(__name__)


class ProjectController:
    """项目 CRUD"""

    @staticmethod
    async def create(data: dict[str, Any]) -> Project:
        project = await Project.create(**data)
        LOGGER.bind(project_id=project.id, name=project.name).info("Project created")
        return project

    @staticmethod
    async def get_by_id(id_: int) -> Project | None:
        return await Project.get_by_id(id_)

    @staticmethod
    async def get_list(page: int = 1, size: int = 10) -> tuple[list[Project], int]:
        offset = (page - 1) * size
        items = await Project.filter(delete_time=None).offset(offset).limit(size).order_by("-id")
        total = await Project.filter(delete_time=None).count()
        return list(items), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> Project | None:
        project = await Project.get_by_id(id_)
        if not project:
            return None
        await project.update_from_dict(data)
        await project.save()
        LOGGER.bind(project_id=id_).info("Project updated")
        return project

    @staticmethod
    async def delete(id_: int) -> bool:
        project = await Project.get_by_id(id_)
        if not project:
            return False
        await project.soft_delete()
        LOGGER.bind(project_id=id_).info("Project deleted")
        return True
