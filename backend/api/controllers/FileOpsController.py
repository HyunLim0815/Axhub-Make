"""文件操作控制器"""

import os
import shutil
from pathlib import Path
from typing import Any

import structlog

from config.db import get_settings

LOGGER = structlog.get_logger(__name__)


class FileOpsController:
    """文件操作：上传/复制/重命名/删除"""

    @staticmethod
    def _get_base_path() -> Path:
        """获取文件存储基础目录"""
        settings = get_settings()
        base = getattr(settings, "DATA_DIR", "data")
        p = Path(base) / "files"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    async def upload(file_content: bytes, filename: str, sub_dir: str = "") -> dict[str, Any]:
        """上传文件到指定子目录"""
        base = FileOpsController._get_base_path()
        target_dir = base / sub_dir if sub_dir else base
        target_dir.mkdir(parents=True, exist_ok=True)
        # 避免文件名冲突
        filepath = target_dir / filename
        counter = 1
        while filepath.exists():
            stem = filepath.stem
            suffix = filepath.suffix
            filepath = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        filepath.write_bytes(file_content)
        size = len(file_content)
        LOGGER.bind(filename=str(filepath), size=size).info("File uploaded")
        return {
            "filename": filepath.name,
            "path": str(filepath.relative_to(base.parent)),
            "size": size,
        }

    @staticmethod
    async def copy(source: str, destination: str) -> bool:
        """复制文件或目录"""
        base = FileOpsController._get_base_path()
        src_path = base.parent / source
        dst_path = base.parent / destination
        if not src_path.exists():
            return False
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_dir():
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)
        LOGGER.bind(source=source, destination=destination).info("File copied")
        return True

    @staticmethod
    async def rename(old_path: str, new_path: str) -> bool:
        """重命名文件或目录"""
        base = FileOpsController._get_base_path()
        src = base.parent / old_path
        dst = base.parent / new_path
        if not src.exists():
            return False
        dst.parent.mkdir(parents=True, exist_ok=True)
        src.rename(dst)
        LOGGER.bind(old_path=old_path, new_path=new_path).info("File renamed")
        return True

    @staticmethod
    async def delete(path: str) -> bool:
        """删除文件或目录"""
        base = FileOpsController._get_base_path()
        target = base.parent / path
        if not target.exists():
            return False
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        LOGGER.bind(path=path).info("File deleted")
        return True

    @staticmethod
    async def list_dir(sub_dir: str = "") -> list[dict[str, Any]]:
        """列出指定子目录下的文件列表"""
        base = FileOpsController._get_base_path()
        target_dir = base.parent / sub_dir if sub_dir else base.parent
        if not target_dir.exists() or not target_dir.is_dir():
            return []
        result = []
        for entry in sorted(target_dir.iterdir()):
            stat = entry.stat()
            result.append({
                "name": entry.name,
                "path": str(entry.relative_to(base.parent)),
                "size": stat.st_size,
                "is_dir": entry.is_dir(),
                "modified_time": stat.st_mtime,
            })
        return result
