import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.assets import Building, Floor, Room, Bed


async def overview(db: AsyncSession, tenant_id: uuid.UUID):
    b = (await db.execute(select(func.count(Building.id)).where(Building.tenant_id == tenant_id))).scalar_one()
    r = (await db.execute(select(func.count(Room.id)).where(Room.tenant_id == tenant_id))).scalar_one()
    bed_total = (await db.execute(select(func.count(Bed.id)).where(Bed.tenant_id == tenant_id))).scalar_one()
    bed_vacant = (await db.execute(select(func.count(Bed.id)).where(Bed.tenant_id == tenant_id, Bed.status == "vacant"))).scalar_one()
    bed_maint = (await db.execute(select(func.count(Bed.id)).where(Bed.tenant_id == tenant_id, Bed.status == "maintenance"))).scalar_one()
    return {"buildings": b, "rooms": r, "beds": bed_total, "vacant_beds": bed_vacant, "maintenance_beds": bed_maint}
