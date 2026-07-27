"""发布控制器 — 业务逻辑"""

from typing import Any

import structlog

from models.publish import PublishChannel, PublishRecord

LOGGER = structlog.get_logger(__name__)


class PublishController:
    """发布通道 CRUD + 部署"""

    @staticmethod
    async def get_channels() -> list[PublishChannel]:
        channels = await PublishChannel.filter(delete_time=None).order_by("id")
        return list(channels)

    @staticmethod
    async def update_channel(id_: int, data: dict[str, Any]) -> PublishChannel | None:
        channel = await PublishChannel.filter(id=id_, delete_time=None).first()
        if not channel:
            return None
        await channel.update_from_dict(data)
        await channel.save()
        LOGGER.bind(channel_id=id_).info("Channel updated")
        return channel

    @staticmethod
    async def deploy(channel_id: int, summary: str = "") -> PublishRecord | None:
        """部署到指定通道"""
        channel = await PublishChannel.filter(id=channel_id, delete_time=None).first()
        if not channel:
            return None

        next_version = (channel.current_version or 0) + 1

        # 创建发布记录
        record = await PublishRecord.create(
            channel_id=channel_id,
            version=next_version,
            summary=summary or f"v{next_version}",
            status="published",
        )

        # 更新通道版本
        channel.current_version = next_version
        channel.status = "published"
        await channel.save()

        LOGGER.bind(
            channel_id=channel_id,
            version=next_version,
        ).info("Deploy completed")
        return record

    @staticmethod
    async def get_records(
        channel_id: int | None = None,
        limit: int = 10,
    ) -> list[PublishRecord]:
        query = PublishRecord.all().order_by("-version")
        if channel_id:
            query = query.filter(channel_id=channel_id)
        records = await query.limit(limit).select_related("channel")
        return list(records)

    @staticmethod
    async def get_dashboard() -> dict[str, Any]:
        """获取仪表盘数据"""
        channels = await PublishController.get_channels()
        records = await PublishController.get_records(limit=10)

        return {
            "channels": [
                {
                    "id": c.id,
                    "name": c.name,
                    "type": c.type,
                    "base_url": c.base_url,
                    "current_version": c.current_version,
                    "status": c.status,
                }
                for c in channels
            ],
            "latest_records": [
                {
                    "id": r.id,
                    "channel_id": r.channel_id,
                    "version": r.version,
                    "summary": r.summary,
                    "status": r.status,
                    "create_time": r.create_time.isoformat() if r.create_time else None,
                }
                for r in records
            ],
            "total_deploys": len(records),
        }
