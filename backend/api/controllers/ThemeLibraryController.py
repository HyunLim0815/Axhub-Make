"""主题库控制器 — 业务逻辑"""

from typing import Any

import httpx
import structlog

from models.template_library import ThemeLibraryEntry

LOGGER = structlog.get_logger(__name__)


class ThemeLibraryController:
    """主题库 CRUD + 导入 + 搜索"""

    @staticmethod
    async def create(data: dict[str, Any]) -> ThemeLibraryEntry:
        entry = await ThemeLibraryEntry.create(**data)
        LOGGER.bind(entry_id=entry.id, name=entry.name).info("Theme created")
        return entry

    @staticmethod
    async def get_by_id(id_: int) -> ThemeLibraryEntry | None:
        return await ThemeLibraryEntry.get_by_id(id_)

    @staticmethod
    async def get_list(
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[ThemeLibraryEntry], int]:
        query = ThemeLibraryEntry.filter(delete_time=None)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> ThemeLibraryEntry | None:
        entry = await ThemeLibraryEntry.get_by_id(id_)
        if not entry:
            return None
        await entry.update_from_dict(data)
        await entry.save()
        LOGGER.bind(entry_id=id_).info("Theme updated")
        return entry

    @staticmethod
    async def delete(id_: int) -> bool:
        entry = await ThemeLibraryEntry.get_by_id(id_)
        if not entry:
            return False
        await entry.soft_delete()
        LOGGER.bind(entry_id=id_).info("Theme deleted")
        return True

    @staticmethod
    async def import_from_url(source_url: str, name: str) -> ThemeLibraryEntry:
        """从 URL 导入主题内容"""
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(source_url)
            resp.raise_for_status()
            data = resp.json()
        entry = await ThemeLibraryEntry.create(
            name=name,
            description=f"Imported from {source_url}",
            tokens=data.get("tokens", {}),
            colors=data.get("colors", {}),
            typography=data.get("typography", {}),
        )
        LOGGER.bind(entry_id=entry.id, name=name, source_url=source_url).info(
            "Theme imported"
        )
        return entry

    @staticmethod
    async def search(q: str) -> list[ThemeLibraryEntry]:
        """搜索主题（名称/描述模糊匹配）"""
        items = await ThemeLibraryEntry.filter(
            delete_time=None,
        ).filter(
            name__icontains=q
        ).order_by("-id").limit(20)
        if len(items) < 20:
            desc_items = await ThemeLibraryEntry.filter(
                delete_time=None,
                description__icontains=q,
            ).order_by("-id").limit(20 - len(items))
            existing_ids = {e.id for e in items}
            items.extend(e for e in desc_items if e.id not in existing_ids)
        return items
