"""云发布与 Axhub 集成 API 路由"""

from fastapi import APIRouter

from api.controllers.AxhubController import AxhubController
from api.controllers.CloudPublishController import CloudPublishController
from api.responses.Base import ApiResponse
from api.schemas.cloud_publish import (
    AxhubConnectRequest,
    CloudPublishConfigCreate,
    CloudPublishConfigUpdate,
    PublishRequest,
)

config_router = APIRouter(prefix="/v1/cloud-publishing", tags=["cloud-publish"])
axhub_router = APIRouter(prefix="/v1/axhub", tags=["axhub"])


# ─── 云发布配置 CRUD ───


@config_router.get("/config", response_model=ApiResponse)
async def list_configs():
    configs = await CloudPublishController.get_configs()
    return ApiResponse(data=[
        {
            "id": c.id,
            "name": c.name,
            "provider": c.provider,
            "config": c.config,
            "enabled": c.enabled,
            "create_time": c.create_time.isoformat() if c.create_time else None,
        }
        for c in configs
    ])


@config_router.post("/config", response_model=ApiResponse, status_code=201)
async def create_config(body: CloudPublishConfigCreate):
    config = await CloudPublishController.create_config(body.model_dump())
    return ApiResponse(
        code=201,
        message="config created",
        data={
            "id": config.id,
            "name": config.name,
            "provider": config.provider,
        },
    )


@config_router.put("/config/{id}", response_model=ApiResponse)
async def update_config(id: int, body: CloudPublishConfigUpdate):
    config = await CloudPublishController.update_config(id, body.model_dump(exclude_none=True))
    if not config:
        return ApiResponse(code=404, message="config not found")
    return ApiResponse(data={
        "id": config.id,
        "name": config.name,
        "provider": config.provider,
        "enabled": config.enabled,
    })


@config_router.delete("/config/{id}", response_model=ApiResponse)
async def delete_config(id: int):
    ok = await CloudPublishController.delete_config(id)
    if not ok:
        return ApiResponse(code=404, message="config not found")
    return ApiResponse(message="config deleted")


@config_router.post("/publish", response_model=ApiResponse)
async def publish(body: PublishRequest):
    result = await CloudPublishController.publish(body.config_id, body.summary)
    if not result["success"]:
        return ApiResponse(code=404, message=result["message"])
    return ApiResponse(data=result)


# ─── Axhub 集成 ───


@axhub_router.get("/status", response_model=ApiResponse)
async def axhub_status():
    status = await AxhubController.get_status()
    return ApiResponse(data=status)


@axhub_router.post("/connect", response_model=ApiResponse)
async def axhub_connect(body: AxhubConnectRequest):
    result = await AxhubController.connect(
        code=body.code,
        redirect_uri=body.redirect_uri,
        is_enterprise=body.is_enterprise,
        enterprise_url=body.enterprise_url,
    )
    return ApiResponse(data=result)


@axhub_router.post("/disconnect", response_model=ApiResponse)
async def axhub_disconnect():
    ok = await AxhubController.disconnect()
    if not ok:
        return ApiResponse(code=404, message="not connected")
    return ApiResponse(message="disconnected")


@axhub_router.post("/publish", response_model=ApiResponse)
async def axhub_publish(body: PublishRequest):
    result = await AxhubController.publish(body.config_id, body.summary)
    if not result["success"]:
        return ApiResponse(code=400, message=result["message"])
    return ApiResponse(data=result)
