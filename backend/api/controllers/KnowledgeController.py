"""知识库控制器 — 业务逻辑"""

from typing import Any

import structlog

from models.knowledge import KnowledgeEntry

LOGGER = structlog.get_logger(__name__)


class KnowledgeController:
    """知识库 CRUD + 搜索"""

    @staticmethod
    async def create(data: dict[str, Any]) -> KnowledgeEntry:
        entry = await KnowledgeEntry.create(**data)
        LOGGER.bind(entry_id=entry.id, type=entry.type, title=entry.title).info("Knowledge entry created")
        return entry

    @staticmethod
    async def get_by_id(id_: int) -> KnowledgeEntry | None:
        return await KnowledgeEntry.get_by_id(id_)

    @staticmethod
    async def get_list(
        type_filter: str | None = None,
        project_id: int | None = None,
        scope: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[KnowledgeEntry], int]:
        query = KnowledgeEntry.filter(delete_time=None)
        if type_filter:
            query = query.filter(type=type_filter)
        if project_id:
            query = query.filter(project_id=project_id)
        if scope:
            query = query.filter(scope=scope)
        offset = (page - 1) * size
        entries = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(entries), total

    @staticmethod
    async def get_team_knowledge(
        page: int = 1, size: int = 10,
    ) -> tuple[list[KnowledgeEntry], int]:
        return await KnowledgeController.get_list(
            scope="team", page=page, size=size,
        )

    @staticmethod
    async def get_project_knowledge(
        project_id: int, page: int = 1, size: int = 10,
    ) -> tuple[list[KnowledgeEntry], int]:
        return await KnowledgeController.get_list(
            project_id=project_id, page=page, size=size,
        )

    @staticmethod
    async def search(q: str) -> list[KnowledgeEntry]:
        """全文搜索（简单实现：标题/内容 LIKE）"""
        entries = await KnowledgeEntry.filter(
            delete_time=None,
        ).filter(
            title__icontains=q
        ).order_by("-id").limit(20)
        # 如果标题匹配不够，补充内容匹配
        if len(entries) < 20:
            content_entries = await KnowledgeEntry.filter(
                delete_time=None,
                content__icontains=q,
            ).order_by("-id").limit(20 - len(entries))
            existing_ids = {e.id for e in entries}
            entries.extend(e for e in content_entries if e.id not in existing_ids)
        return entries

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> KnowledgeEntry | None:
        entry = await KnowledgeEntry.get_by_id(id_)
        if not entry:
            return None
        await entry.update_from_dict(data)
        await entry.save()
        LOGGER.bind(entry_id=id_).info("Knowledge entry updated")
        return entry

    @staticmethod
    async def delete(id_: int) -> bool:
        entry = await KnowledgeEntry.get_by_id(id_)
        if not entry:
            return False
        await entry.soft_delete()
        LOGGER.bind(entry_id=id_).info("Knowledge entry deleted")
        return True
