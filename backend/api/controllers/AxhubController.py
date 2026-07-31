"""Axhub 在线集成控制器"""
from datetime import datetime, timedelta
from typing import Any, Optional

import structlog

from models.cloud_publish import AxhubConnection

LOGGER = structlog.get_logger(__name__)


class AxhubController:
    """Axhub 在线 OAuth + 发布"""

    @staticmethod
    async def get_status() -> dict[str, Any]:
        conn = await AxhubConnection.filter(delete_time=None, is_active=True).first()
        if not conn:
            return {"connected": False, "user_info": {}, "is_enterprise": False}
        return {
            "connected": True,
            "user_info": conn.user_info,
            "is_enterprise": conn.is_enterprise,
            "expires_at": conn.expires_at.isoformat() if conn.expires_at else None,
        }

    @staticmethod
    async def connect(code: str, redirect_uri: str = "", is_enterprise: bool = False, enterprise_url: str = "") -> dict[str, Any]:
        # 模拟 OAuth 连接
        conn, _ = await AxhubConnection.get_or_create(
            defaults={
                "name": "Axhub Connection",
                "access_token": f"mock_token_{code[:8]}...",
                "refresh_token": f"mock_refresh_{datetime.now().timestamp()}",
                "expires_at": datetime.now() + timedelta(days=30),
                "user_info": {"name": "User", "email": "user@example.com"},
                "is_enterprise": is_enterprise,
                "enterprise_url": enterprise_url,
                "is_active": True,
            }
        )
        if not conn:
            conn.is_active = True
            conn.access_token = f"mock_token_{code[:8]}..."
            conn.expires_at = datetime.now() + timedelta(days=30)
            await conn.save()
        LOGGER.info("Axhub connected")
        return {"success": True, "message": "Connected to Axhub"}

    @staticmethod
    async def disconnect() -> bool:
        conn = await AxhubConnection.filter(delete_time=None, is_active=True).first()
        if not conn:
            return False
        conn.is_active = False
        await conn.save()
        LOGGER.info("Axhub disconnected")
        return True

    @staticmethod
    async def publish(project_id: int, summary: str = "") -> dict[str, Any]:
        conn = await AxhubConnection.filter(delete_time=None, is_active=True).first()
        if not conn:
            return {"success": False, "message": "Not connected to Axhub"}
        LOGGER.bind(project_id=project_id).info("Axhub publish triggered")
        return {
            "success": True,
            "url": f"https://axhub.example.com/p/{project_id}",
            "message": f"Published to Axhub: {summary or 'v1'}",
        }
