"""
基础模型 — BaseModel

所有领域模型的基类，提供:
- 自增主键 (id)
- 时间戳 (create_time, update_time)
- 软删除 (delete_time)
- 基础 CRUD 快捷方法
"""

from datetime import datetime
from typing import Optional

from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    """基础模型 — 所有领域模型继承此类"""

    id = fields.IntField(pk=True, auto_increment=True)
    create_time = fields.DatetimeField(auto_now_add=True)
    update_time = fields.DatetimeField(auto_now=True)
    delete_time = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
        ordering = ["-id"]

    async def soft_delete(self) -> None:
        """软删除：设置 delete_time 为当前时间"""
        self.delete_time = datetime.now()
        await self.save(update_fields=["delete_time"])

    @classmethod
    async def get_active(cls, **kwargs: dict) -> Optional[Model]:
        """获取未软删除的单个记录"""
        return await cls.filter(delete_time=None, **kwargs).first()

    @classmethod
    async def get_by_id(cls, id_: int) -> Optional[Model]:
        """按 ID 获取未软删除的记录"""
        return await cls.filter(id=id_, delete_time=None).first()
