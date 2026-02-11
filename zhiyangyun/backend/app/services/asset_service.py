from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Building, Floor, Room, Bed
from app.models.elder import Elder
from app.schemas.asset import BuildingCreate, FloorCreate, RoomCreate, BedCreate


class AssetService:
    def list_buildings(self, db: Session, tenant_id: str):
        return db.scalars(select(Building).where(Building.tenant_id == tenant_id)).all()

    def create_building(self, db: Session, tenant_id: str, payload: BuildingCreate):
        item = Building(tenant_id=tenant_id, name=payload.name, code=payload.code)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_floors(self, db: Session, tenant_id: str):
        return db.scalars(select(Floor).where(Floor.tenant_id == tenant_id)).all()

    def create_floor(self, db: Session, tenant_id: str, payload: FloorCreate):
        item = Floor(tenant_id=tenant_id, building_id=payload.building_id, floor_no=payload.floor_no, name=payload.name)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_rooms(self, db: Session, tenant_id: str):
        return db.scalars(select(Room).where(Room.tenant_id == tenant_id)).all()

    def create_room(self, db: Session, tenant_id: str, payload: RoomCreate):
        item = Room(
            tenant_id=tenant_id,
            building_id=payload.building_id,
            floor_id=payload.floor_id,
            room_no=payload.room_no,
            room_type=payload.room_type,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_beds(self, db: Session, tenant_id: str):
        return db.scalars(select(Bed).where(Bed.tenant_id == tenant_id)).all()

    def create_bed(self, db: Session, tenant_id: str, payload: BedCreate):
        qr = f"BED:{tenant_id}:{payload.room_id}:{payload.bed_no}"
        item = Bed(tenant_id=tenant_id, room_id=payload.room_id, bed_no=payload.bed_no, qr_code=qr)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_bed_status(self, db: Session, tenant_id: str, bed_id: str, status: str):
        item = db.scalar(select(Bed).where(Bed.id == bed_id, Bed.tenant_id == tenant_id))
        if not item:
            return None
        if status == "occupied":
            linked = db.scalar(
                select(Elder.id).where(
                    Elder.tenant_id == tenant_id,
                    Elder.bed_id == bed_id,
                    Elder.status == "admitted",
                )
            )
            if not linked:
                raise ValueError("床位占用必须通过 M2 入院/转床流程完成")
        item.status = status
        db.commit()
        db.refresh(item)
        return item

    def occupancy_summary(self, db: Session, tenant_id: str):
        beds = db.scalars(select(Bed).where(Bed.tenant_id == tenant_id)).all()
        admitted_elders = db.scalars(
            select(Elder).where(Elder.tenant_id == tenant_id, Elder.status == "admitted")
        ).all()
        admitted_bed_ids = {e.bed_id for e in admitted_elders if e.bed_id}

        by_status = {
            "vacant": 0,
            "reserved": 0,
            "occupied": 0,
            "maintenance": 0,
            "other": 0,
        }
        anomalies = []
        for bed in beds:
            if bed.status in by_status:
                by_status[bed.status] += 1
            else:
                by_status["other"] += 1

            if bed.status == "occupied" and bed.id not in admitted_bed_ids:
                anomalies.append({"bed_id": bed.id, "issue": "床位标记为 occupied 但无在院长者绑定"})
            if bed.status != "occupied" and bed.id in admitted_bed_ids:
                anomalies.append({"bed_id": bed.id, "issue": "床位存在在院长者绑定但状态不是 occupied"})

        total = len(beds)
        occupied = by_status["occupied"]
        occupancy_rate = round((occupied / total) * 100, 2) if total else 0

        return {
            "total_beds": total,
            "occupied_beds": occupied,
            "vacant_beds": by_status["vacant"],
            "reserved_beds": by_status["reserved"],
            "maintenance_beds": by_status["maintenance"],
            "occupancy_rate": occupancy_rate,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
        }

    def reconcile_bed_status(self, db: Session, tenant_id: str):
        beds = db.scalars(select(Bed).where(Bed.tenant_id == tenant_id)).all()
        admitted_elders = db.scalars(
            select(Elder).where(Elder.tenant_id == tenant_id, Elder.status == "admitted")
        ).all()
        admitted_bed_ids = {e.bed_id for e in admitted_elders if e.bed_id}

        fixed = []
        for bed in beds:
            target = bed.status
            if bed.id in admitted_bed_ids and bed.status != "occupied":
                target = "occupied"
            if bed.id not in admitted_bed_ids and bed.status == "occupied":
                target = "vacant"
            if target != bed.status:
                fixed.append({"bed_id": bed.id, "from": bed.status, "to": target})
                bed.status = target

        if fixed:
            db.commit()
        return {"fixed_count": len(fixed), "fixed": fixed}
