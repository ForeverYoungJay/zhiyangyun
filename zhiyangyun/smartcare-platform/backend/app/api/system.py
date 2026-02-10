from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/api/v1/system", tags=["system"])


@router.get("/info")
async def system_info():
    return {
        "name": settings.app_name,
        "env": settings.env,
        "version": "0.1.0",
        "phase": "Phase1",
    }
