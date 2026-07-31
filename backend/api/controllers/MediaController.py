"""媒体资源控制器 — 上传 / 列表 / 删除 / 文件读取"""

import os
import uuid
from typing import Any, Optional

import structlog

from models.media import MediaFile

LOGGER = structlog.get_logger(__name__)

# 媒体文件存储根目录
MEDIA_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "media")


def _ensure_storage_dir(sub_dir: str = "") -> str:
    """确保存储目录存在，返回完整路径"""
    target = os.path.join(MEDIA_ROOT, sub_dir) if sub_dir else MEDIA_ROOT
    os.makedirs(target, exist_ok=True)
    return target


class MediaController:
    """媒体资源 CRUD"""

    @staticmethod
    async def list(
        folder: str = "",
        project_id: Optional[int] = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[MediaFile], int]:
        """获取媒体文件列表（分页）"""
        query = MediaFile.filter(delete_time=None)
        if folder:
            query = query.filter(folder=folder)
        if project_id is not None:
            query = query.filter(project_id=project_id)
        total = await query.count()
        items = await query.offset((page - 1) * size).limit(size).order_by("-id")
        LOGGER.bind(folder=folder, project_id=project_id, total=total).debug(
            "Media files listed"
        )
        return list(items), total

    @staticmethod
    async def upload(
        file_content: bytes,
        filename: str,
        mime_type: str,
        folder: str = "",
        project_id: Optional[int] = None,
    ) -> MediaFile:
        """上传文件：保存到磁盘并创建数据库记录"""
        # 生成唯一存储文件名，避免冲突
        ext = os.path.splitext(filename)[1]
        stored_name = f"{uuid.uuid4().hex}{ext}"
        sub_dir = folder.strip("/")
        target_dir = _ensure_storage_dir(sub_dir)
        stored_path = os.path.join(target_dir, stored_name)

        # 写入文件
        with open(stored_path, "wb") as f:
            f.write(file_content)

        # 数据库相对路径
        relative_path = os.path.join(sub_dir, stored_name).replace("\\", "/") if sub_dir else stored_name

        record = await MediaFile.create(
            filename=filename,
            filepath=relative_path,
            mime_type=mime_type,
            size=len(file_content),
            folder=folder,
            project_id=project_id,
        )
        LOGGER.bind(
            media_id=record.id,
            filename=filename,
            size=len(file_content),
            folder=folder,
        ).info("Media file uploaded")
        return record

    @staticmethod
    async def create_folder(name: str, parent: str = "") -> dict[str, Any]:
        """创建分类文件夹（实际在存储根下建目录）"""
        sub_path = os.path.join(parent, name).replace("\\", "/")
        _ensure_storage_dir(sub_path)
        LOGGER.bind(folder=sub_path).info("Media folder created")
        return {"name": name, "parent": parent, "path": sub_path}

    @staticmethod
    async def delete(id_: int) -> bool:
        """删除媒体文件（软删除 + 删除磁盘文件）"""
        record = await MediaFile.get_by_id(id_)
        if not record:
            return False

        # 删除磁盘文件
        file_path = os.path.join(MEDIA_ROOT, record.filepath)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as exc:
                LOGGER.bind(media_id=id_, filepath=record.filepath, error=str(exc)).warning(
                    "Failed to delete media file from disk"
                )

        await record.soft_delete()
        LOGGER.bind(media_id=id_, filename=record.filename).info("Media file deleted")
        return True

    @staticmethod
    async def get_file(filepath: str) -> Optional[bytes]:
        """根据相对路径读取文件内容"""
        full_path = os.path.normpath(os.path.join(MEDIA_ROOT, filepath))
        # 安全检查：确保文件在 MEDIA_ROOT 之下
        if not full_path.startswith(os.path.normpath(MEDIA_ROOT)):
            LOGGER.bind(filepath=filepath).warning("Path traversal attempt detected")
            return None
        if not os.path.isfile(full_path):
            LOGGER.bind(filepath=filepath).warning("Media file not found on disk")
            return None
        with open(full_path, "rb") as f:
            return f.read()
