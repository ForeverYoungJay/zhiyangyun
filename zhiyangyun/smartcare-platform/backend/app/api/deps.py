import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.models.auth import User, UserRole, Role, RolePermission, Permission

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        user_id = uuid.UUID(payload["sub"])
        tenant_id = uuid.UUID(payload["tenant_id"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")

    q = select(User).where(User.id == user_id, User.tenant_id == tenant_id, User.is_active.is_(True))
    user = (await db.execute(q)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="user not found")
    return user


def require_permission(permission_code: str):
    async def checker(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
        q = (
            select(Permission.code)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user.id,
                UserRole.tenant_id == user.tenant_id,
                Role.tenant_id == user.tenant_id,
                RolePermission.tenant_id == user.tenant_id,
            )
        )
        codes = {r[0] for r in (await db.execute(q)).all()}
        if permission_code not in codes:
            raise HTTPException(status_code=403, detail="forbidden")
        return True

    return checker
