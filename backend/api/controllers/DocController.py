"""文档控制器 — 文档 & 模板业务逻辑"""

import json
import os
import re
from typing import Any

import structlog

from models.document import Document, DocumentTemplate

LOGGER = structlog.get_logger(__name__)

# 文档上传存储路径
DOCS_STORAGE_DIR = "data/docs"


class DocController:
    """文档 & 模板 CRUD"""

    # ── 文档 CRUD ──

    @staticmethod
    async def create(data: dict[str, Any]) -> Document:
        """创建文档"""
        project_id = data.pop("project_id", None)
        if project_id is not None:
            data["project_id"] = project_id
        document = await Document.create(**data)
        LOGGER.bind(document_id=document.id, title=document.title).info("Document created")
        return document

    @staticmethod
    async def get_by_id(id_: int) -> Document | None:
        """按 ID 获取文档"""
        return await Document.get_by_id(id_)

    @staticmethod
    async def get_list(
        page: int = 1,
        size: int = 10,
        project_id: int | None = None,
        keyword: str | None = None,
    ) -> tuple[list[Document], int]:
        """获取文档列表，支持按项目和关键词筛选"""
        qs = Document.filter(delete_time=None)
        if project_id is not None:
            qs = qs.filter(project_id=project_id)
        if keyword:
            qs = qs.filter(title__icontains=keyword)
        offset = (page - 1) * size
        items = await qs.offset(offset).limit(size).order_by("-id")
        total = await qs.count()
        return list(items), total

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> Document | None:
        """更新文档"""
        document = await Document.get_by_id(id_)
        if not document:
            return None
        # 处理 project_id
        if "project_id" in data:
            project_id = data.pop("project_id")
            data["project_id"] = project_id
        await document.update_from_dict(data)
        await document.save()
        LOGGER.bind(document_id=id_).info("Document updated")
        return document

    @staticmethod
    async def delete(id_: int) -> bool:
        """删除文档（软删除）"""
        document = await Document.get_by_id(id_)
        if not document:
            return False
        await document.soft_delete()
        LOGGER.bind(document_id=id_).info("Document deleted")
        return True

    @staticmethod
    async def upload_file(file_bytes: bytes, filename: str, mime_type: str, title: str = "") -> Document:
        """上传文档文件并创建 Document 记录

        将文件保存到 data/docs/ 目录，并创建对应的文档记录。
        """
        # 确保存储目录存在
        os.makedirs(DOCS_STORAGE_DIR, exist_ok=True)

        # 生成唯一文件名避免冲突
        import uuid
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(DOCS_STORAGE_DIR, unique_name)

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # 创建文档记录
        doc_title = title or filename
        document = await Document.create(
            title=doc_title,
            content="",
            file_path=file_path,
            mime_type=mime_type,
            tags=[],
        )
        LOGGER.bind(
            document_id=document.id, filename=filename, size=len(file_bytes),
        ).info("Document file uploaded")
        return document

    # ── 模板 CRUD ──

    @staticmethod
    async def create_template(data: dict[str, Any]) -> DocumentTemplate:
        """创建文档模板"""
        template = await DocumentTemplate.create(**data)
        LOGGER.bind(template_id=template.id, name=template.name).info("DocumentTemplate created")
        return template

    @staticmethod
    async def get_template_by_id(id_: int) -> DocumentTemplate | None:
        """按 ID 获取模板"""
        return await DocumentTemplate.get_by_id(id_)

    @staticmethod
    async def get_template_list(
        page: int = 1,
        size: int = 10,
        category: str | None = None,
    ) -> tuple[list[DocumentTemplate], int]:
        """获取模板列表，支持按分类筛选"""
        qs = DocumentTemplate.filter(delete_time=None)
        if category:
            qs = qs.filter(category=category)
        offset = (page - 1) * size
        items = await qs.offset(offset).limit(size).order_by("-id")
        total = await qs.count()
        return list(items), total

    @staticmethod
    async def delete_template(id_: int) -> bool:
        """删除模板（软删除）"""
        template = await DocumentTemplate.get_by_id(id_)
        if not template:
            return False
        await template.soft_delete()
        LOGGER.bind(template_id=id_).info("DocumentTemplate deleted")
        return True

    # ── 引用检查 ──

    @staticmethod
    async def check_references(content: str) -> list[dict[str, Any]]:
        """扫描内容中引用的其他文档 ID

        匹配模式: {id:N} 或 [doc:N] 或 #doc:N
        返回引用到的文档信息列表。
        """
        # 提取所有可能的文档 ID 引用
        pattern = r"(?:\{id:(\d+)\}|\[doc:(\d+)\]|#doc:(\d+))"
        matches = re.findall(pattern, content)
        # 展平匹配结果
        ref_ids = set()
        for groups in matches:
            for g in groups:
                if g:
                    ref_ids.add(int(g))

        if not ref_ids:
            return []

        references = []
        for rid in sorted(ref_ids):
            doc = await Document.get_by_id(rid)
            if doc:
                references.append({
                    "id": doc.id,
                    "title": doc.title,
                    "exists": True,
                })
            else:
                references.append({
                    "id": rid,
                    "title": None,
                    "exists": False,
                })

        LOGGER.bind(reference_count=len(references)).info("References checked")
        return references
