"""
数据迁移工具 — 从 Node.js JSON 文件导入 PostgreSQL

支持导入的数据源:
- annotation-source.json → Prototype + Annotation + AnnotationVersion
- .axhub/knowledge-base.json → KnowledgeEntry
- .axhub/publish.json → PublishChannel + PublishRecord

用法:
    python -m utils.tools.migrate --dir /path/to/project
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import structlog

# 在独立运行时添加项目根到 PATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

LOGGER = structlog.get_logger(__name__)


class DataMigrator:
    """JSON → PostgreSQL 迁移器"""

    def __init__(self, project_dir: str) -> None:
        self.project_dir = Path(project_dir)
        self.stats: dict[str, int] = {
            "prototypes": 0,
            "annotations": 0,
            "versions": 0,
            "knowledge": 0,
            "channels": 0,
            "records": 0,
        }

    async def run(self) -> dict[str, int]:
        """执行全部迁移"""
        LOGGER.bind(project_dir=str(self.project_dir)).info("Starting data migration")

        await self._migrate_annotations()
        await self._migrate_knowledge()
        await self._migrate_publish()

        LOGGER.bind(stats=self.stats).info("Migration completed")
        return self.stats

    # ── annotation-source.json → Prototype + Annotation ──

    async def _migrate_annotations(self) -> None:
        """迁移标注数据"""
        source_paths = list(self.project_dir.rglob("annotation-source.json"))
        if not source_paths:
            LOGGER.info("No annotation-source.json found, skipping")
            return

        from models.annotation import Annotation, AnnotationVersion
        from models.prototype import Prototype

        for source_path in source_paths:
            try:
                data = json.loads(source_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError) as e:
                LOGGER.bind(path=str(source_path), error=str(e)).warning("Skipping invalid file")
                continue

            nodes = data.get("data", {}).get("nodes", [])
            if not nodes:
                continue

            # 创建原型
            prototype_name = data.get("data", {}).get("prototypeName", source_path.parent.name)
            prototype = await Prototype.create(
                name=prototype_name,
                page_id=data.get("data", {}).get("pageId", ""),
            )
            self.stats["prototypes"] += 1

            # 创建标注
            for node in nodes:
                await Annotation.create(
                    prototype=prototype,
                    title=node.get("title", ""),
                    annotation_text=node.get("annotationText", ""),
                    markdown=data.get("markdownMap", {}).get(node.get("id", ""), ""),
                    color=node.get("color", "#1677FF"),
                    scope=node.get("scope", "element"),
                    locator=node.get("locator", {}),
                    page_id=node.get("pageId", ""),
                )
                self.stats["annotations"] += 1

            # 创建版本记录
            versions = data.get("data", {}).get("versions", [])
            for ver in versions:
                await AnnotationVersion.create(
                    prototype=prototype,
                    version=ver.get("version", 1),
                    diff=ver.get("diff", []),
                    summary=ver.get("summary", ""),
                    tags=ver.get("tags", []),
                    status=ver.get("status", "draft"),
                )
                self.stats["versions"] += 1

            LOGGER.bind(
                file=source_path.name,
                prototype=prototype_name,
                annotations=len(nodes),
            ).info("Annotation source migrated")

    # ── knowledge-base.json → KnowledgeEntry ──

    async def _migrate_knowledge(self) -> None:
        """迁移知识库数据"""
        kb_path = self.project_dir / ".axhub" / "knowledge-base.json"
        if not kb_path.exists():
            LOGGER.info("No knowledge-base.json found, skipping")
            return

        from models.knowledge import KnowledgeEntry

        try:
            data = json.loads(kb_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            LOGGER.bind(error=str(e)).warning("Failed to read knowledge-base.json")
            return

        entries = data.get("entries", [])
        for entry in entries:
            await KnowledgeEntry.create(
                type=entry.get("type", "decision"),
                title=entry.get("title", ""),
                content=entry.get("content", ""),
                tags=entry.get("tags", []),
                source=entry.get("source", ""),
            )
            self.stats["knowledge"] += 1

        LOGGER.bind(count=len(entries)).info("Knowledge base migrated")

    # ── publish.json → PublishChannel + PublishRecord ──

    async def _migrate_publish(self) -> None:
        """迁移发布数据"""
        pub_path = self.project_dir / ".axhub" / "publish.json"
        if not pub_path.exists():
            LOGGER.info("No publish.json found, skipping")
            return

        from models.publish import PublishChannel, PublishRecord

        try:
            data = json.loads(pub_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            LOGGER.bind(error=str(e)).warning("Failed to read publish.json")
            return

        channels = data.get("channels", [])
        for ch in channels:
            channel = await PublishChannel.create(
                name=ch.get("name", "未命名"),
                type=ch.get("type", "development"),
                base_url=ch.get("baseUrl", ""),
                access_control=ch.get("accessControl", "team"),
                current_version=ch.get("currentVersion", 0),
                status=ch.get("status", "pending"),
            )
            self.stats["channels"] += 1

        records = data.get("records", [])
        for rec in records:
            await PublishRecord.create(
                channel_id=rec.get("channelId", 0),
                version=rec.get("version", 1),
                summary=rec.get("summary", ""),
                status=rec.get("status", "published"),
                error=rec.get("error", ""),
            )
            self.stats["records"] += 1

        LOGGER.bind(
            channels=len(channels), records=len(records)
        ).info("Publish data migrated")


async def main() -> None:
    """CLI 入口"""
    parser = argparse.ArgumentParser(description="Axhub Make 数据迁移工具")
    parser.add_argument(
        "--dir",
        required=True,
        help="项目目录路径（包含 .axhub/ 和 prototypes/）",
    )
    parser.add_argument(
        "--db-url",
        default="",
        help="数据库 URL（默认从 .env 读取）",
    )
    args = parser.parse_args()

    # 初始化 Tortoise
    from tortoise import Tortoise

    from config.tortoise import get_tortoise_config

    config = get_tortoise_config()
    if args.db_url:
        config["connections"]["default"] = args.db_url

    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()

    try:
        migrator = DataMigrator(args.dir)
        stats = await migrator.run()
        print(f"\n迁移完成:")
        for key, count in stats.items():
            print(f"  {key}: {count}")
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
