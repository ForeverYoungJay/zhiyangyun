from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.elder import CrmLead, Elder, ElderChangeLog
from app.schemas.elder import LeadCreate, ElderCreate, ElderAdmit, ElderTransfer, ElderDischarge


class ElderService:
    def list_leads(self, db: Session, tenant_id: str):
        return db.scalars(select(CrmLead).where(CrmLead.tenant_id == tenant_id)).all()

    def create_lead(self, db: Session, tenant_id: str, payload: LeadCreate):
        item = CrmLead(tenant_id=tenant_id, name=payload.name, phone=payload.phone, source_channel=payload.source_channel, notes=payload.notes)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_elders(self, db: Session, tenant_id: str):
        return db.scalars(select(Elder).where(Elder.tenant_id == tenant_id)).all()

    def create_elder(self, db: Session, tenant_id: str, payload: ElderCreate):
        item = Elder(
            tenant_id=tenant_id,
            lead_id=payload.lead_id,
            elder_no=payload.elder_no,
            name=payload.name,
            gender=payload.gender,
            birth_date=payload.birth_date,
            id_card=payload.id_card,
            care_level=payload.care_level,
            status="assessed",
        )
        db.add(item)
        db.flush()
        db.add(ElderChangeLog(tenant_id=tenant_id, elder_id=item.id, action="create", detail="建档完成"))
        db.commit()
        db.refresh(item)
        return item

    def admit(self, db: Session, tenant_id: str, elder_id: str, payload: ElderAdmit):
        elder = db.scalar(select(Elder).where(Elder.id == elder_id, Elder.tenant_id == tenant_id))
        bed = db.scalar(select(Bed).where(Bed.id == payload.bed_id, Bed.tenant_id == tenant_id))
        if not elder or not bed:
            return None
        if elder.status not in ["assessed", "discharged"]:
            return None
        if bed.status not in ["vacant", "reserved"]:
            return None

        bed.status = "occupied"
        elder.status = "admitted"
        elder.admission_date = payload.admission_date
        elder.building_id = payload.building_id
        elder.floor_id = payload.floor_id
        elder.room_id = payload.room_id
        elder.bed_id = payload.bed_id
        db.add(ElderChangeLog(tenant_id=tenant_id, elder_id=elder.id, action="admit", detail=f"入住床位:{bed.id}"))
        db.commit()
        db.refresh(elder)
        return elder

    def transfer(self, db: Session, tenant_id: str, elder_id: str, payload: ElderTransfer):
        elder = db.scalar(select(Elder).where(Elder.id == elder_id, Elder.tenant_id == tenant_id))
        new_bed = db.scalar(select(Bed).where(Bed.id == payload.bed_id, Bed.tenant_id == tenant_id))
        if not elder or elder.status != "admitted" or not new_bed or new_bed.status != "vacant":
            return None

        if elder.bed_id:
            old_bed = db.scalar(select(Bed).where(Bed.id == elder.bed_id, Bed.tenant_id == tenant_id))
            if old_bed:
                old_bed.status = "vacant"

        new_bed.status = "occupied"
        elder.building_id = payload.building_id
        elder.floor_id = payload.floor_id
        elder.room_id = payload.room_id
        elder.bed_id = payload.bed_id
        db.add(ElderChangeLog(tenant_id=tenant_id, elder_id=elder.id, action="transfer", detail=f"转床:{payload.bed_id}"))
        db.commit()
        db.refresh(elder)
        return elder

    def discharge(self, db: Session, tenant_id: str, elder_id: str, payload: ElderDischarge):
        elder = db.scalar(select(Elder).where(Elder.id == elder_id, Elder.tenant_id == tenant_id))
        if not elder or elder.status != "admitted":
            return None

        if elder.bed_id:
            bed = db.scalar(select(Bed).where(Bed.id == elder.bed_id, Bed.tenant_id == tenant_id))
            if bed:
                bed.status = "vacant"

        elder.status = "discharged"
        elder.discharge_date = payload.discharge_date
        db.add(ElderChangeLog(tenant_id=tenant_id, elder_id=elder.id, action="discharge", detail=payload.note))
        db.commit()
        db.refresh(elder)
        return elder

    def logs(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(ElderChangeLog).where(ElderChangeLog.tenant_id == tenant_id, ElderChangeLog.elder_id == elder_id)).all()
