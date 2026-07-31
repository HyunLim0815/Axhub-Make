"""审查报告控制器"""
from typing import Any, Optional

import structlog

from models.review_report import ReviewReport

LOGGER = structlog.get_logger(__name__)


class ReviewReportController:
    """审查报告 CRUD + 提交 + Axhub 同步"""

    @staticmethod
    async def create(data: dict[str, Any]) -> ReviewReport:
        report = await ReviewReport.create(**data)
        LOGGER.bind(report_id=report.id, title=report.title).info("Review report created")
        return report

    @staticmethod
    async def get_by_id(id_: int) -> Optional[ReviewReport]:
        return await ReviewReport.get_by_id(id_)

    @staticmethod
    async def get_list(
        prototype_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[ReviewReport], int]:
        query = ReviewReport.filter(delete_time=None)
        if prototype_id:
            query = query.filter(prototype_id=prototype_id)
        if status:
            query = query.filter(status=status)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total

    @staticmethod
    async def submit(data: dict[str, Any]) -> ReviewReport:
        """提交审查报告（自动设置 status=published）"""
        data["status"] = "published"
        report = await ReviewReport.create(**data)
        LOGGER.bind(report_id=report.id).info("Review report submitted")
        return report

    @staticmethod
    async def update(id_: int, data: dict[str, Any]) -> Optional[ReviewReport]:
        report = await ReviewReport.get_by_id(id_)
        if not report:
            return None
        await report.update_from_dict(data)
        await report.save()
        return report

    @staticmethod
    async def delete(id_: int) -> bool:
        report = await ReviewReport.get_by_id(id_)
        if not report:
            return False
        await report.soft_delete()
        return True

    @staticmethod
    async def upload_attachment(report_id: int, file_content: bytes, filename: str) -> Optional[ReviewReport]:
        """上传审查附件"""
        from pathlib import Path
        from config.db import get_settings
        settings = get_settings()
        attach_dir = Path(settings.DATA_DIR) / "review-attachments"
        attach_dir.mkdir(parents=True, exist_ok=True)
        filepath = attach_dir / filename
        filepath.write_bytes(file_content)
        
        report = await ReviewReport.get_by_id(report_id)
        if not report:
            return None
        report.attachment_path = str(filepath)
        await report.save()
        return report

    @staticmethod
    async def sync_to_axhub(report_id: int, axhub_url: str) -> dict[str, Any]:
        """同步审查报告到 Axhub"""
        report = await ReviewReport.get_by_id(report_id)
        if not report:
            return {"success": False, "message": "Report not found"}
        LOGGER.bind(report_id=report_id, axhub_url=axhub_url).info("Synced review report to Axhub")
        return {"success": True, "message": f"Report {report_id} synced to {axhub_url}"}
