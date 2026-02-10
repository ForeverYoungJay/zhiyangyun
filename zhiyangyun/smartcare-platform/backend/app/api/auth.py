from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.models.auth import User
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginReq
from app.schemas.common import ApiResp
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=ApiResp)
async def login(payload: LoginReq, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == payload.username))).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid username or password")
    token = create_access_token(str(user.id), str(user.tenant_id))
    return ApiResp(data={
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "username": user.username,
            "real_name": user.real_name,
            "tenant_id": str(user.tenant_id),
        },
    })


@router.get("/me", response_model=ApiResp)
async def me(user=Depends(get_current_user)):
    return ApiResp(data={
        "id": str(user.id),
        "username": user.username,
        "real_name": user.real_name,
        "tenant_id": str(user.tenant_id),
    })
