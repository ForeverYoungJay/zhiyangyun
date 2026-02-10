import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.api.deps import get_current_user, require_permission
from app.schemas.common import ApiResp
from app.schemas.assets import *
from app.models.assets import Building, Floor, Room, Bed
from app.services.assets_service import overview

router = APIRouter(prefix="/api/v1", tags=["assets"])


def _dict(obj):
    d = obj.__dict__.copy()
    d.pop("_sa_instance_state", None)
    return {k: (str(v) if isinstance(v, uuid.UUID) else v) for k, v in d.items()}


@router.get("/assets/overview", response_model=ApiResp)
async def get_overview(db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.read"))):
    return ApiResp(data=await overview(db, user.tenant_id))


@router.get("/buildings", response_model=ApiResp)
async def list_buildings(db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.read"))):
    rows = (await db.execute(select(Building).where(Building.tenant_id == user.tenant_id).order_by(Building.created_at.desc()))).scalars().all()
    return ApiResp(data=[_dict(x) for x in rows])


@router.post("/buildings", response_model=ApiResp)
async def create_building(payload: BuildingCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = Building(tenant_id=user.tenant_id, code=payload.code, name=payload.name, address=payload.address)
    db.add(row)
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.put("/buildings/{bid}", response_model=ApiResp)
async def update_building(bid: str, payload: BuildingUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = (await db.execute(select(Building).where(Building.id == uuid.UUID(bid), Building.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(row, k, v)
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.delete("/buildings/{bid}", response_model=ApiResp)
async def delete_building(bid: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.delete"))):
    building_id = uuid.UUID(bid)
    has_floor = (await db.execute(select(Floor).where(Floor.building_id == building_id, Floor.tenant_id == user.tenant_id))).scalar_one_or_none()
    has_room = (await db.execute(select(Room).where(Room.building_id == building_id, Room.tenant_id == user.tenant_id))).scalar_one_or_none()
    if has_floor or has_room: raise HTTPException(400, "building has children")
    row = (await db.execute(select(Building).where(Building.id == building_id, Building.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    await db.delete(row); await db.commit()
    return ApiResp(message="deleted")


@router.get("/floors", response_model=ApiResp)
async def list_floors(building_id: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.read"))):
    cond = [Floor.tenant_id == user.tenant_id]
    if building_id: cond.append(Floor.building_id == uuid.UUID(building_id))
    rows = (await db.execute(select(Floor).where(and_(*cond)).order_by(Floor.floor_no.asc()))).scalars().all()
    return ApiResp(data=[_dict(x) for x in rows])


@router.post("/floors", response_model=ApiResp)
async def create_floor(payload: FloorCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    b = (await db.execute(select(Building).where(Building.id == uuid.UUID(payload.building_id), Building.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not b: raise HTTPException(400, "building not found")
    row = Floor(tenant_id=user.tenant_id, building_id=b.id, floor_no=payload.floor_no, name=payload.name)
    db.add(row); await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.put("/floors/{fid}", response_model=ApiResp)
async def update_floor(fid: str, payload: FloorUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = (await db.execute(select(Floor).where(Floor.id == uuid.UUID(fid), Floor.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(row, k, v)
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.delete("/floors/{fid}", response_model=ApiResp)
async def delete_floor(fid: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.delete"))):
    floor_id = uuid.UUID(fid)
    has_room = (await db.execute(select(Room).where(Room.floor_id == floor_id, Room.tenant_id == user.tenant_id))).scalar_one_or_none()
    if has_room: raise HTTPException(400, "floor has rooms")
    row = (await db.execute(select(Floor).where(Floor.id == floor_id, Floor.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    await db.delete(row); await db.commit()
    return ApiResp(message="deleted")


@router.get("/rooms", response_model=ApiResp)
async def list_rooms(building_id: str | None = None, floor_id: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.read"))):
    cond = [Room.tenant_id == user.tenant_id]
    if building_id: cond.append(Room.building_id == uuid.UUID(building_id))
    if floor_id: cond.append(Room.floor_id == uuid.UUID(floor_id))
    rows = (await db.execute(select(Room).where(and_(*cond)).order_by(Room.room_no.asc()))).scalars().all()
    return ApiResp(data=[_dict(x) for x in rows])


@router.post("/rooms", response_model=ApiResp)
async def create_room(payload: RoomCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = Room(tenant_id=user.tenant_id, building_id=uuid.UUID(payload.building_id), floor_id=uuid.UUID(payload.floor_id), room_no=payload.room_no, room_type=payload.room_type, capacity=payload.capacity, qr_code=f"ROOM-{payload.room_no}")
    db.add(row); await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.put("/rooms/{rid}", response_model=ApiResp)
async def update_room(rid: str, payload: RoomUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = (await db.execute(select(Room).where(Room.id == uuid.UUID(rid), Room.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(row, k, v)
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.delete("/rooms/{rid}", response_model=ApiResp)
async def delete_room(rid: str, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.delete"))):
    room_id = uuid.UUID(rid)
    has_bed = (await db.execute(select(Bed).where(Bed.room_id == room_id, Bed.tenant_id == user.tenant_id))).scalar_one_or_none()
    if has_bed: raise HTTPException(400, "room has beds")
    row = (await db.execute(select(Room).where(Room.id == room_id, Room.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    await db.delete(row); await db.commit()
    return ApiResp(message="deleted")


@router.get("/beds", response_model=ApiResp)
async def list_beds(room_id: str | None = None, status: str | None = None, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.read"))):
    cond = [Bed.tenant_id == user.tenant_id]
    if room_id: cond.append(Bed.room_id == uuid.UUID(room_id))
    if status: cond.append(Bed.status == status)
    rows = (await db.execute(select(Bed).where(and_(*cond)).order_by(Bed.bed_no.asc()))).scalars().all()
    return ApiResp(data=[_dict(x) for x in rows])


@router.post("/beds", response_model=ApiResp)
async def create_bed(payload: BedCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = Bed(tenant_id=user.tenant_id, room_id=uuid.UUID(payload.room_id), bed_no=payload.bed_no, status=payload.status, qr_code=f"BED-{payload.bed_no}")
    db.add(row); await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.put("/beds/{bid}", response_model=ApiResp)
async def update_bed(bid: str, payload: BedUpdate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = (await db.execute(select(Bed).where(Bed.id == uuid.UUID(bid), Bed.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    for k, v in payload.model_dump(exclude_unset=True).items(): setattr(row, k, v)
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))


@router.post("/beds/{bid}/status", response_model=ApiResp)
async def set_bed_status(bid: str, payload: BedStatusReq, db: AsyncSession = Depends(get_db), user=Depends(get_current_user), _=Depends(require_permission("assets.write"))):
    row = (await db.execute(select(Bed).where(Bed.id == uuid.UUID(bid), Bed.tenant_id == user.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404, "not found")
    row.status = payload.status
    await db.commit(); await db.refresh(row)
    return ApiResp(data=_dict(row))
