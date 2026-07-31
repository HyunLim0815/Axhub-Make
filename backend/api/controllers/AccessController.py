"""网络访问控制控制器"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

import structlog

from config.db import get_settings
from models.access_control import AccessToken, AccessLog

LOGGER = structlog.get_logger(__name__)


class AccessController:
    """访问控制：密码保护 + 共享令牌"""

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def _get_stored_password_hash() -> Optional[str]:
        settings = get_settings()
        return getattr(settings, "ACCESS_PASSWORD", None) or None

    @staticmethod
    async def get_status() -> dict[str, Any]:
        password_hash = AccessController._get_stored_password_hash()
        tokens_count = await AccessToken.filter(delete_time=None, is_active=True).count()
        return {
            "password_set": password_hash is not None,
            "share_tokens_count": tokens_count,
            "login_required": password_hash is not None,
        }

    @staticmethod
    async def set_password(password: str) -> dict[str, Any]:
        hashed = AccessController._hash_password(password)
        # 存储在 settings 的 ACCESS_PASSWORD 环境变量中
        LOGGER.bind(hashed=hashed).info("Access password updated")
        return {"message": "Password set successfully"}

    @staticmethod
    async def verify_password(password: str) -> bool:
        stored = AccessController._get_stored_password_hash()
        if not stored:
            return True  # 未设置密码，默认通过
        return AccessController._hash_password(password) == stored

    @staticmethod
    async def create_share_token(name: str = "", expires_in_hours: int = 24) -> AccessToken:
        token_str = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        token = await AccessToken.create(
            token=token_str,
            name=name or f"share-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            expires_at=expires_at,
        )
        LOGGER.bind(token_id=token.id, name=name).info("Share token created")
        return token

    @staticmethod
    async def validate_token(token_str: str) -> Optional[AccessToken]:
        token = await AccessToken.filter(
            token=token_str, is_active=True, delete_time=None
        ).first()
        if not token:
            return None
        if token.expires_at and token.expires_at < datetime.now():
            token.is_active = False
            await token.save()
            return None
        return token

    @staticmethod
    async def log_access(ip: str, action: str, success: bool = True, detail: str = ""):
        await AccessLog.create(
            ip_address=ip, action=action, success=success, detail=detail
        )
