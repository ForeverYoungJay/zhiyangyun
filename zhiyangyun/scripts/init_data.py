import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.models import User, Role, Permission, UserRole, RolePermission
from backend.app.models.asset import Building, Floor, Room, Bed

DB_URL = "postgresql+psycopg://postgres:postgres@db:5432/zhiyangyun"
TENANT_ID = "tenant-demo-001"


def run():
    engine = create_engine(DB_URL)
    with Session(engine) as db:
        if db.scalar(select(User).where(User.username == "admin")):
            print("seed exists")
            return

        admin = User(
            id=str(uuid.uuid4()),
            tenant_id=TENANT_ID,
            username="admin",
            password_hash=get_password_hash("Admin@123456"),
            real_name="系统管理员",
            is_active=True,
        )
        role = Role(id=str(uuid.uuid4()), tenant_id=TENANT_ID, code="admin", name="管理员")
        perm_codes = [
            ("asset.building.manage", "楼栋管理"),
            ("asset.floor.manage", "楼层管理"),
            ("asset.room.manage", "房间管理"),
            ("asset.bed.manage", "床位管理"),
        ]
        perms = [Permission(id=str(uuid.uuid4()), tenant_id=TENANT_ID, code=code, name=name) for code, name in perm_codes]

        db.add_all([admin, role, *perms])
        db.flush()

        db.add(UserRole(id=str(uuid.uuid4()), tenant_id=TENANT_ID, user_id=admin.id, role_id=role.id))
        for p in perms:
            db.add(RolePermission(id=str(uuid.uuid4()), tenant_id=TENANT_ID, role_id=role.id, permission_id=p.id))

        b = Building(id=str(uuid.uuid4()), tenant_id=TENANT_ID, name="A栋", code="A")
        db.add(b)
        db.flush()
        f1 = Floor(id=str(uuid.uuid4()), tenant_id=TENANT_ID, building_id=b.id, floor_no=1, name="1层")
        db.add(f1)
        db.flush()
        r1 = Room(
            id=str(uuid.uuid4()),
            tenant_id=TENANT_ID,
            building_id=b.id,
            floor_id=f1.id,
            room_no="101",
            room_type="double",
            status="available",
        )
        db.add(r1)
        db.flush()
        db.add(Bed(id=str(uuid.uuid4()), tenant_id=TENANT_ID, room_id=r1.id, bed_no="1", status="vacant", qr_code=f"BED:{TENANT_ID}:{r1.id}:1"))
        db.commit()
        print("seed done")


if __name__ == "__main__":
    run()
