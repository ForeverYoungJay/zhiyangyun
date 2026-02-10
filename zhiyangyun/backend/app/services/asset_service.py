from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Building, Floor, Room, Bed
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
        item.status = status
        db.commit()
        db.refresh(item)
        return item
