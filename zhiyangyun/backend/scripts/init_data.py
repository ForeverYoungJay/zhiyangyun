import uuid
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import User, Role, Permission, UserRole, RolePermission
from app.models.asset import Building, Floor, Room, Bed
from app.models.elder import CrmLead, Elder

DB_URL = "postgresql+psycopg://postgres:postgres@db:5432/zhiyangyun"
TENANT_ID = "tenant-demo-001"


def run():
    engine = create_engine(DB_URL)
    with Session(engine) as db:
        admin = db.scalar(select(User).where(User.username == "admin"))
        if not admin:
            admin = User(
                id=str(uuid.uuid4()),
                tenant_id=TENANT_ID,
                username="admin",
                password_hash=get_password_hash("Admin@123456"),
                real_name="系统管理员",
                is_active=True,
            )
            db.add(admin)
            db.flush()

        role = db.scalar(select(Role).where(Role.code == "admin"))
        if not role:
            role = Role(id=str(uuid.uuid4()), tenant_id=TENANT_ID, code="admin", name="管理员")
            db.add(role)
            db.flush()

        perm_codes = [
            ("asset.building.manage", "楼栋管理"),
            ("asset.floor.manage", "楼层管理"),
            ("asset.room.manage", "房间管理"),
            ("asset.bed.manage", "床位管理"),
        ]
        perms = []
        for code, name in perm_codes:
            p = db.scalar(select(Permission).where(Permission.code == code))
            if not p:
                p = Permission(id=str(uuid.uuid4()), tenant_id=TENANT_ID, code=code, name=name)
                db.add(p)
                db.flush()
            perms.append(p)

        link = db.scalar(select(UserRole).where(UserRole.user_id == admin.id, UserRole.role_id == role.id))
        if not link:
            db.add(UserRole(id=str(uuid.uuid4()), tenant_id=TENANT_ID, user_id=admin.id, role_id=role.id))

        for p in perms:
            rp = db.scalar(select(RolePermission).where(RolePermission.role_id == role.id, RolePermission.permission_id == p.id))
            if not rp:
                db.add(RolePermission(id=str(uuid.uuid4()), tenant_id=TENANT_ID, role_id=role.id, permission_id=p.id))

        b = db.scalar(select(Building).where(Building.code == "A", Building.tenant_id == TENANT_ID))
        if not b:
            b = Building(id=str(uuid.uuid4()), tenant_id=TENANT_ID, name="A栋", code="A")
            db.add(b)
            db.flush()

        f1 = db.scalar(select(Floor).where(Floor.building_id == b.id, Floor.floor_no == 1, Floor.tenant_id == TENANT_ID))
        if not f1:
            f1 = Floor(id=str(uuid.uuid4()), tenant_id=TENANT_ID, building_id=b.id, floor_no=1, name="1层")
            db.add(f1)
            db.flush()

        r1 = db.scalar(select(Room).where(Room.floor_id == f1.id, Room.room_no == "101", Room.tenant_id == TENANT_ID))
        if not r1:
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

        bed = db.scalar(select(Bed).where(Bed.room_id == r1.id, Bed.bed_no == "1", Bed.tenant_id == TENANT_ID))
        if not bed:
            bed = Bed(id=str(uuid.uuid4()), tenant_id=TENANT_ID, room_id=r1.id, bed_no="1", status="vacant", qr_code=f"BED:{TENANT_ID}:{r1.id}:1")
            db.add(bed)

        lead = db.scalar(select(CrmLead).where(CrmLead.phone == "13800000000", CrmLead.tenant_id == TENANT_ID))
        if not lead:
            lead = CrmLead(id=str(uuid.uuid4()), tenant_id=TENANT_ID, name="张三", phone="13800000000", source_channel="offline", status="new", notes="首访")
            db.add(lead)
            db.flush()

        elder = db.scalar(select(Elder).where(Elder.elder_no == "ELD-0001", Elder.tenant_id == TENANT_ID))
        if not elder:
            elder = Elder(
                id=str(uuid.uuid4()), tenant_id=TENANT_ID, lead_id=lead.id, elder_no="ELD-0001", name="王大爷",
                gender="male", id_card="", care_level="L2", status="assessed"
            )
            db.add(elder)

        db.commit()
        print("seed done")


if __name__ == "__main__":
    run()
