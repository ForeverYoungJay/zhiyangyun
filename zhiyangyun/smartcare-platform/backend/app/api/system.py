from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import ApiResp

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/info", response_model=ApiResp)
async def system_info():
    return ApiResp(data={
        "name": settings.app_name,
        "env": settings.env,
        "version": "0.2.0",
        "phase": "A1-M1",
    })
