"""模板库控制器 — 业务逻辑"""

from typing import Any

import httpx
import structlog

from models.template_library import TemplateLibraryEntry

LOGGER = structlog.get_logger(__name__)


class TemplateLibraryController:
    """模板库 CRUD + 导入 + 搜索"""

    @staticmethod
    async def create(data: dict[str, Any]) -> TemplateLibraryEntry:
        entry = await TemplateLibraryEntry.create(**data)
        LOGGER.bind(entry_id=entry.id, name=entry.name).info("Template created")
        return entry

    @staticmethod
    async def get_by_id(id_: int) -> TemplateLibraryEntry | None:
        return await TemplateLibraryEntry.get_by_id(id_)

    @staticmethod
    async def get_list(
        category: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[TemplateLibraryEntry], int]:
        query = TemplateLibraryEntry.filter(delete_time=None)
        if category:
            query = query.filter(category=category)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> TemplateLibraryEntry | None:
        entry = await TemplateLibraryEntry.get_by_id(id_)
        if not entry:
            return None
        await entry.update_from_dict(data)
        await entry.save()
        LOGGER.bind(entry_id=id_).info("Template updated")
        return entry

    @staticmethod
    async def delete(id_: int) -> bool:
        entry = await TemplateLibraryEntry.get_by_id(id_)
        if not entry:
            return False
        await entry.soft_delete()
        LOGGER.bind(entry_id=id_).info("Template deleted")
        return True

    @staticmethod
    async def import_from_url(source_url: str, name: str) -> TemplateLibraryEntry:
        """从 URL 导入模板内容"""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(source_url)
            resp.raise_for_status()
            content = resp.json()
        entry = await TemplateLibraryEntry.create(
            name=name,
            description=f"Imported from {source_url}",
            content=content,
        )
        LOGGER.bind(entry_id=entry.id, name=name, source_url=source_url).info(
            "Template imported"
        )
        return entry

    @staticmethod
    async def search(q: str) -> list[TemplateLibraryEntry]:
        """搜索模板（名称/描述/标签模糊匹配）"""
        items = await TemplateLibraryEntry.filter(
            delete_time=None,
        ).filter(
            name__icontains=q
        ).order_by("-id").limit(20)
        if len(items) < 20:
            desc_items = await TemplateLibraryEntry.filter(
                delete_time=None,
                description__icontains=q,
            ).order_by("-id").limit(20 - len(items))
            existing_ids = {e.id for e in items}
            items.extend(e for e in desc_items if e.id not in existing_ids)
        return items
