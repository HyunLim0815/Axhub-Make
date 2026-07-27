"""发布 API 路由"""

from fastapi import APIRouter

from api.controllers.PublishController import PublishController
from api.responses.Base import ApiResponse
from api.schemas.publish import ChannelUpdate, DeployCreate

router = APIRouter(prefix="/v1/publish", tags=["publish"])


@router.get("/channels", response_model=ApiResponse)
async def get_channels():
    channels = await PublishController.get_channels()
    return ApiResponse(
        data=[{
            "id": c.id,
            "name": c.name,
            "type": c.type,
            "base_url": c.base_url,
            "access_control": c.access_control,
            "current_version": c.current_version,
            "status": c.status,
        } for c in channels]
    )


@router.put("/channels/{id}", response_model=ApiResponse)
async def update_channel(id: int, body: ChannelUpdate):
    channel = await PublishController.update_channel(id, body.model_dump(exclude_none=True))
    if not channel:
        return ApiResponse(code=404, message="channel not found")
    return ApiResponse(data={
        "id": channel.id,
        "name": channel.name,
        "base_url": channel.base_url,
        "access_control": channel.access_control,
    })


@router.post("/channels/{id}/deploy", response_model=ApiResponse, status_code=201)
async def deploy(id: int, body: DeployCreate = DeployCreate()):
    record = await PublishController.deploy(id, body.summary)
    if not record:
        return ApiResponse(code=404, message="channel not found")
    return ApiResponse(
        code=201,
        message="deployed",
        data={
            "id": record.id,
            "channel_id": record.channel_id,
            "version": record.version,
            "summary": record.summary,
            "status": record.status,
        },
    )


@router.get("/records", response_model=ApiResponse)
async def get_records(channel_id: int | None = None):
    records = await PublishController.get_records(channel_id)
    return ApiResponse(data=[
        {
            "id": r.id,
            "channel_id": r.channel_id,
            "version": r.version,
            "summary": r.summary,
            "status": r.status,
            "created_at": r.create_time.isoformat() if r.create_time else None,
        }
        for r in records
    ])


@router.get("/dashboard", response_model=ApiResponse)
async def dashboard():
    data = await PublishController.get_dashboard()
    return ApiResponse(data=data)
