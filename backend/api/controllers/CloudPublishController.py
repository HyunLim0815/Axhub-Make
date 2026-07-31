"""云发布控制器"""
from datetime import datetime
from typing import Any, Optional

import structlog

from models.cloud_publish import CloudPublishConfig

LOGGER = structlog.get_logger(__name__)


class CloudPublishController:
    """云发布配置管理 + 部署"""

    @staticmethod
    async def get_configs() -> list[CloudPublishConfig]:
        return await CloudPublishConfig.filter(delete_time=None, enabled=True).order_by("id")

    @staticmethod
    async def create_config(data: dict[str, Any]) -> CloudPublishConfig:
        config = await CloudPublishConfig.create(**data)
        LOGGER.bind(config_id=config.id, name=config.name).info("Cloud publish config created")
        return config

    @staticmethod
    async def update_config(id_: int, data: dict[str, Any]) -> Optional[CloudPublishConfig]:
        config = await CloudPublishConfig.filter(id=id_, delete_time=None).first()
        if not config:
            return None
        await config.update_from_dict(data)
        await config.save()
        return config

    @staticmethod
    async def delete_config(id_: int) -> bool:
        config = await CloudPublishConfig.filter(id=id_, delete_time=None).first()
        if not config:
            return False
        await config.soft_delete()
        return True

    @staticmethod
    async def publish(config_id: int, summary: str = "") -> dict[str, Any]:
        config = await CloudPublishConfig.filter(id=config_id, delete_time=None).first()
        if not config:
            return {"success": False, "message": "Config not found"}
        LOGGER.bind(config_id=config_id, provider=config.provider).info("Cloud publish triggered")
        return {
            "success": True,
            "url": f"https://{config.provider}.example.com/p/{config_id}",
            "version": int(datetime.now().timestamp()),
            "message": f"Published to {config.name}",
        }
