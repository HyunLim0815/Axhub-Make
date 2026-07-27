"""
SSE (Server-Sent Events) 流式响应工具

用于 AI 流式输出的统一出口。
"""

import json
from typing import AsyncIterator, Any

from fastapi.responses import StreamingResponse


async def sse_stream(generator: AsyncIterator[str]) -> AsyncIterator[bytes]:
    """将异步迭代器转换为 SSE 格式流

    Args:
        generator: 产生文本块的异步迭代器

    Yields:
        SSE 格式的 bytes

    用法:
        @router.get("/stream")
        async def stream():
            return StreamingResponse(
                sse_stream(my_generator()),
                media_type="text/event-stream",
            )
    """
    try:
        async for chunk in generator:
            yield f"data: {json.dumps({'content': chunk})}\n\n".encode("utf-8")
        yield "data: [DONE]\n\n".encode("utf-8")
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n".encode("utf-8")


def create_sse_response(
    generator: AsyncIterator[str],
) -> StreamingResponse:
    """创建 SSE 响应

    Args:
        generator: 产生文本块的异步迭代器

    Returns:
        StreamingResponse (media_type: text/event-stream)
    """
    return StreamingResponse(
        sse_stream(generator),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
