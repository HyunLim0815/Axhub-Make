"""原型控制器 — 业务逻辑"""

from typing import Any

import structlog

from models.prototype import Prototype

LOGGER = structlog.get_logger(__name__)


class PrototypeController:
    """原型 CRUD"""

    @staticmethod
    async def create(data: dict[str, Any]) -> Prototype:
        prototype = await Prototype.create(**data)
        LOGGER.bind(prototype_id=prototype.id, name=prototype.name).info("Prototype created")
        return prototype

    @staticmethod
    async def get_by_id(id_: int) -> Prototype | None:
        return await Prototype.get_by_id(id_)

    @staticmethod
    async def get_list(page: int = 1, size: int = 10) -> tuple[list[Prototype], int]:
        offset = (page - 1) * size
        prototypes = await Prototype.filter(delete_time=None).offset(offset).limit(size)
        total = await Prototype.filter(delete_time=None).count()
        return list(prototypes), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> Prototype | None:
        prototype = await Prototype.get_by_id(id_)
        if not prototype:
            return None
        await prototype.update_from_dict(data)
        await prototype.save()
        LOGGER.bind(prototype_id=id_).info("Prototype updated")
        return prototype

    @staticmethod
    async def delete(id_: int) -> bool:
        prototype = await Prototype.get_by_id(id_)
        if not prototype:
            return False
        await prototype.soft_delete()
        LOGGER.bind(prototype_id=id_).info("Prototype deleted")
        return True
