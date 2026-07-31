"""WebSocket 桥接模块 — Canvas 同步 / 预览桥接 / MCP 桥接

对应 V1 的 canvasBridge.ts / previewBridge.ts / axhubCanvasMcp.ts / axhubPreviewMcp.ts。
每个 bridge 维护一个连接的客户端集合，支持广播消息。
"""

import asyncio
import json
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

LOGGER = structlog.get_logger(__name__)

router = APIRouter(tags=["websocket"])


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self) -> None:
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, ws: WebSocket) -> str:
        await ws.accept()
        conn_id = uuid.uuid4().hex[:12]
        self.active_connections[conn_id] = ws
        LOGGER.bind(conn_id=conn_id, total=len(self.active_connections)).info(
            "WebSocket connected"
        )
        return conn_id

    def disconnect(self, conn_id: str) -> None:
        self.active_connections.pop(conn_id, None)
        LOGGER.bind(conn_id=conn_id, total=len(self.active_connections)).info(
            "WebSocket disconnected"
        )

    async def broadcast(self, message: dict[str, Any]) -> None:
        """向所有连接广播消息"""
        data = json.dumps(message, ensure_ascii=False)
        dead: list[str] = []
        for conn_id, ws in self.active_connections.items():
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(conn_id)
        for conn_id in dead:
            self.disconnect(conn_id)

    async def send_to(self, conn_id: str, message: dict[str, Any]) -> bool:
        ws = self.active_connections.get(conn_id)
        if not ws:
            return False
        try:
            await ws.send_text(json.dumps(message, ensure_ascii=False))
            return True
        except Exception:
            self.disconnect(conn_id)
            return False


canvas_manager = ConnectionManager()
preview_manager = ConnectionManager()
mcp_manager = ConnectionManager()


async def _bridge_loop(ws: WebSocket, manager: ConnectionManager, kind: str) -> None:
    """通用的桥接消息循环"""
    conn_id = await manager.connect(ws)
    await manager.send_to(conn_id, {"type": "hello", "conn_id": conn_id, "kind": kind})
    try:
        while True:
            data = await ws.receive_text()
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                payload = {"type": "raw", "content": data}
            LOGGER.bind(conn_id=conn_id, type=payload.get("type", "?")).debug(
                "Bridge message received"
            )
            await manager.broadcast(
                {"from": conn_id, "kind": kind, **payload}
            )
    except WebSocketDisconnect:
        manager.disconnect(conn_id)
    except Exception as exc:
        LOGGER.warning("Bridge loop error", error=str(exc))
        manager.disconnect(conn_id)


@router.websocket("/api/canvas-bridge")
async def canvas_bridge(ws: WebSocket) -> None:
    """Canvas 实时同步桥接"""
    await _bridge_loop(ws, canvas_manager, "canvas")


@router.websocket("/api/preview-bridge")
async def preview_bridge(ws: WebSocket) -> None:
    """预览桥接 — 原型预览页与编辑器实时同步"""
    await _bridge_loop(ws, preview_manager, "preview")


@router.websocket("/api/axhub-canvas-mcp")
async def axhub_canvas_mcp(ws: WebSocket) -> None:
    """Canvas MCP Token 桥接（对应 V1 axhubCanvasMcp.ts）"""
    await _bridge_loop(ws, mcp_manager, "canvas-mcp")


@router.websocket("/api/axhub-preview-mcp")
async def axhub_preview_mcp(ws: WebSocket) -> None:
    """Preview MCP Token 桥接（对应 V1 axhubPreviewMcp.ts）"""
    await _bridge_loop(ws, mcp_manager, "preview-mcp")


@router.websocket("/api/opencode-bridge")
async def opencode_bridge(ws: WebSocket) -> None:
    """OpenCode 上下文桥接"""
    await _bridge_loop(ws, mcp_manager, "opencode")


@router.get("/api/ws/clients")
async def ws_clients() -> dict[str, Any]:
    """WebSocket 客户端列表（诊断用）"""
    return {
        "canvas": list(canvas_manager.active_connections.keys()),
        "preview": list(preview_manager.active_connections.keys()),
        "mcp": list(mcp_manager.active_connections.keys()),
    }
