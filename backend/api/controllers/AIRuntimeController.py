"""AI 运行时与任务管理控制器"""
import time
from typing import Any, Optional

import structlog

from ai.llm import LLMService
from ai.router import ModelRouter
from models.ai_runtime import AIRun, AIGenerationTask

LOGGER = structlog.get_logger(__name__)


class AIRuntimeController:
    """AI 运行时管理：Runs + 生成任务"""

    @staticmethod
    async def create_run(data: dict[str, Any]) -> AIRun:
        run = await AIRun.create(**data)
        LOGGER.bind(run_id=run.id, agent_type=data.get("agent_type")).info("AI Run created")
        return run

    @staticmethod
    async def get_run(id_: int) -> Optional[AIRun]:
        return await AIRun.get_by_id(id_)

    @staticmethod
    async def get_runs(
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[AIRun], int]:
        query = AIRun.filter(delete_time=None)
        if project_id:
            query = query.filter(project_id=project_id)
        if status:
            query = query.filter(status=status)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total

    @staticmethod
    async def execute_run(run_id: int) -> Optional[AIRun]:
        """执行 AI Run（模拟执行）"""
        run = await AIRun.get_by_id(run_id)
        if not run:
            return None
        run.status = "running"
        await run.save()
        start = time.time()
        try:
            llm = LLMService()
            router = ModelRouter()
            model = router.route(run.input_data.get("prompt", ""), {})
            messages = [{"role": "user", "content": run.input_data.get("prompt", "")}]
            result = await llm.chat(messages, model=model)
            run.status = "completed"
            run.output_data = {"content": result}
            run.model_used = model
        except Exception as e:
            run.status = "failed"
            run.error = str(e)
        run.duration_ms = int((time.time() - start) * 1000)
        await run.save()
        return run

    @staticmethod
    async def get_artifact_history(project_id: Optional[int] = None, limit: int = 20) -> list[AIRun]:
        query = AIRun.filter(delete_time=None, status="completed")
        if project_id:
            query = query.filter(project_id=project_id)
        items = await query.order_by("-id").limit(limit)
        return list(items)

    # ── 生成任务 ──
    @staticmethod
    async def create_task(data: dict[str, Any]) -> AIGenerationTask:
        task = await AIGenerationTask.create(**data)
        LOGGER.bind(task_id=task.id, type=data.get("type")).info("Generation task created")
        return task

    @staticmethod
    async def get_tasks(
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[AIGenerationTask], int]:
        query = AIGenerationTask.filter(delete_time=None)
        if project_id:
            query = query.filter(project_id=project_id)
        if status:
            query = query.filter(status=status)
        offset = (page - 1) * size
        items = await query.offset(offset).limit(size).order_by("-id")
        total = await query.count()
        return list(items), total
