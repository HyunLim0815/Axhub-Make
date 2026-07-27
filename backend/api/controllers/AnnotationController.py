"""标注控制器 — 业务逻辑"""

from typing import Any

import structlog

from models.annotation import Annotation, AnnotationVersion

LOGGER = structlog.get_logger(__name__)


class AnnotationController:
    """标注 CRUD + 版本管理"""

    @staticmethod
    async def create(data: dict[str, Any]) -> Annotation:
        annotation = await Annotation.create(**data)
        LOGGER.bind(annotation_id=annotation.id, prototype_id=data.get("prototype_id")).info("Annotation created")
        return annotation

    @staticmethod
    async def get_by_id(id_: int) -> Annotation | None:
        return await Annotation.get_by_id(id_)

    @staticmethod
    async def get_list(
        prototype_id: int | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Annotation], int]:
        query = Annotation.filter(delete_time=None)
        if prototype_id:
            query = query.filter(prototype_id=prototype_id)
        offset = (page - 1) * size
        annotations = await query.offset(offset).limit(size).select_related("prototype")
        total = await query.count()
        return list(annotations), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> Annotation | None:
        annotation = await Annotation.get_by_id(id_)
        if not annotation:
            return None
        await annotation.update_from_dict(data)
        await annotation.save()
        LOGGER.bind(annotation_id=id_).info("Annotation updated")
        return annotation

    @staticmethod
    async def delete(id_: int) -> bool:
        annotation = await Annotation.get_by_id(id_)
        if not annotation:
            return False
        await annotation.soft_delete()
        LOGGER.bind(annotation_id=id_).info("Annotation deleted")
        return True


class AnnotationVersionController:
    """版本管理"""

    @staticmethod
    async def create_version(
        prototype_id: int,
        summary: str,
        tags: list[str] | None = None,
    ) -> AnnotationVersion:
        # 获取当前最大版本号
        last = (
            await AnnotationVersion.filter(prototype_id=prototype_id)
            .order_by("-version")
            .first()
        )
        next_version = (last.version + 1) if last else 1

        version = await AnnotationVersion.create(
            prototype_id=prototype_id,
            version=next_version,
            diff=[],
            summary=summary,
            tags=tags or [],
        )
        LOGGER.bind(
            prototype_id=prototype_id,
            version=next_version,
        ).info("Annotation version created")
        return version

    @staticmethod
    async def get_versions(
        prototype_id: int,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[AnnotationVersion], int]:
        query = AnnotationVersion.filter(prototype_id=prototype_id)
        offset = (page - 1) * size
        versions = await query.offset(offset).limit(size).order_by("-version")
        total = await query.count()
        return list(versions), total

    @staticmethod
    async def rollback(prototype_id: int, target_version: int) -> AnnotationVersion | None:
        """回滚到指定版本（创建一条新的回滚记录）"""
        # 验证目标版本存在
        target = await AnnotationVersion.filter(
            prototype_id=prototype_id, version=target_version
        ).first()
        if not target:
            return None

        # 创建回滚版本记录
        last = (
            await AnnotationVersion.filter(prototype_id=prototype_id)
            .order_by("-version")
            .first()
        )
        next_version = (last.version + 1) if last else 1

        rollback = await AnnotationVersion.create(
            prototype_id=prototype_id,
            version=next_version,
            diff=[],
            summary=f"回滚到 v{target_version}",
            tags=["rollback"],
        )
        LOGGER.bind(
            prototype_id=prototype_id,
            from_version=next_version - 1,
            to_version=target_version,
        ).info("Annotation version rollback")
        return rollback
