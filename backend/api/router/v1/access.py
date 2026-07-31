"""访问控制 API 路由 — 密码保护 + 共享令牌"""

from fastapi import APIRouter, Request

from api.controllers.AccessController import AccessController
from api.responses.Base import ApiResponse
from api.schemas.access import (
    LoginRequest,
    PasswordSetRequest,
    ShareTokenRequest,
    TokenValidateRequest,
)

router = APIRouter(prefix="/v1/access", tags=["access"])


def _client_ip(request: Request) -> str:
    """获取客户端 IP"""
    if request.client:
        return request.client.host
    return "unknown"


@router.get("/status", response_model=ApiResponse)
async def get_status():
    status = await AccessController.get_status()
    return ApiResponse(data=status)


@router.post("/password", response_model=ApiResponse)
async def set_password(body: PasswordSetRequest):
    await AccessController.set_password(body.password)
    return ApiResponse(message="password set successfully")


@router.post("/login", response_model=ApiResponse)
async def login(body: LoginRequest, request: Request):
    ok = await AccessController.verify_password(body.password)
    await AccessController.log_access(
        ip=_client_ip(request),
        action="login",
        success=ok,
        detail="" if ok else "invalid password",
    )
    if not ok:
        return ApiResponse(code=401, message="invalid password")
    return ApiResponse(data={"success": True})


@router.post("/share-token", response_model=ApiResponse, status_code=201)
async def create_share_token(body: ShareTokenRequest, request: Request):
    token = await AccessController.create_share_token(
        name=body.name, expires_in_hours=body.expires_in_hours
    )
    await AccessController.log_access(
        ip=_client_ip(request),
        action="share",
        success=True,
        detail=f"token_id={token.id}",
    )
    return ApiResponse(
        code=201,
        message="created",
        data={
            "id": token.id,
            "token": token.token,
            "name": token.name,
            "scope": token.scope,
            "expires_at": token.expires_at.isoformat() if token.expires_at else None,
        },
    )


@router.post("/validate", response_model=ApiResponse)
async def validate_token(body: TokenValidateRequest, request: Request):
    token = await AccessController.validate_token(body.token)
    ok = token is not None
    await AccessController.log_access(
        ip=_client_ip(request),
        action="api_call",
        success=ok,
        detail="token invalid" if not ok else f"token_id={token.id}",
    )
    if not ok:
        return ApiResponse(code=401, message="invalid token")
    return ApiResponse(data={"valid": True, "id": token.id, "scope": token.scope})
