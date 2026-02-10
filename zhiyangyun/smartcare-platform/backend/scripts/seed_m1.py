import asyncio
import uuid
from sqlalchemy import select
from app.db.session import SessionLocal
from app.models.auth import User, Role, Permission, UserRole, RolePermission
from app.core.security import hash_password

TENANT = uuid.UUID("11111111-1111-1111-1111-111111111111")


async def main():
    async with SessionLocal() as db:
        # permissions
        for code, name in [("assets.read", "资产查看"), ("assets.write", "资产编辑"), ("assets.delete", "资产删除")]:
            exists = (await db.execute(select(Permission).where(Permission.code == code))).scalar_one_or_none()
            if not exists:
                db.add(Permission(code=code, name=name))

        await db.flush()

        role = (await db.execute(select(Role).where(Role.tenant_id == TENANT, Role.code == "admin"))).scalar_one_or_none()
        if not role:
            role = Role(tenant_id=TENANT, code="admin", name="管理员")
            db.add(role)
            await db.flush()

        user = (await db.execute(select(User).where(User.username == "admin"))).scalar_one_or_none()
        if not user:
            user = User(
                tenant_id=TENANT,
                username="admin",
                password_hash=hash_password("Admin@123"),
                real_name="系统管理员",
                is_active=True,
            )
            db.add(user)
            await db.flush()

        perms = (await db.execute(select(Permission))).scalars().all()
        for p in perms:
            rp = (await db.execute(select(RolePermission).where(RolePermission.tenant_id == TENANT, RolePermission.role_id == role.id, RolePermission.permission_id == p.id))).scalar_one_or_none()
            if not rp:
                db.add(RolePermission(tenant_id=TENANT, role_id=role.id, permission_id=p.id))

        ur = (await db.execute(select(UserRole).where(UserRole.tenant_id == TENANT, UserRole.user_id == user.id, UserRole.role_id == role.id))).scalar_one_or_none()
        if not ur:
            db.add(UserRole(tenant_id=TENANT, user_id=user.id, role_id=role.id))

        await db.commit()
        print("seed done: admin/Admin@123")


if __name__ == "__main__":
    asyncio.run(main())
