from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.care import ServiceItem, CarePackage, CarePackageItem, ElderPackage, CareTask
from app.schemas.care import (
    ServiceItemCreate,
    CarePackageCreate,
    CarePackageItemCreate,
    ElderPackageCreate,
    TaskGenerateRequest,
)


class CareService:
    def list_items(self, db: Session, tenant_id: str):
        return db.scalars(select(ServiceItem).where(ServiceItem.tenant_id == tenant_id)).all()

    def create_item(self, db: Session, tenant_id: str, payload: ServiceItemCreate):
        item = ServiceItem(
            tenant_id=tenant_id,
            name=payload.name,
            category=payload.category,
            unit_price=payload.unit_price,
            duration_min=payload.duration_min,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_packages(self, db: Session, tenant_id: str):
        return db.scalars(select(CarePackage).where(CarePackage.tenant_id == tenant_id)).all()

    def create_package(self, db: Session, tenant_id: str, payload: CarePackageCreate):
        item = CarePackage(tenant_id=tenant_id, name=payload.name, period=payload.period)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def create_package_item(self, db: Session, tenant_id: str, payload: CarePackageItemCreate):
        item = CarePackageItem(
            tenant_id=tenant_id,
            package_id=payload.package_id,
            item_id=payload.item_id,
            quantity=payload.quantity,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def subscribe_elder_package(self, db: Session, tenant_id: str, payload: ElderPackageCreate):
        item = ElderPackage(
            tenant_id=tenant_id,
            elder_id=payload.elder_id,
            package_id=payload.package_id,
            start_date=payload.start_date,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def list_tasks(self, db: Session, tenant_id: str):
        return db.scalars(select(CareTask).where(CareTask.tenant_id == tenant_id)).all()

    def generate_tasks(self, db: Session, tenant_id: str, payload: TaskGenerateRequest):
        sub = db.scalar(select(ElderPackage).where(ElderPackage.id == payload.elder_package_id, ElderPackage.tenant_id == tenant_id))
        if not sub:
            return []
        items = db.scalars(select(CarePackageItem).where(CarePackageItem.package_id == sub.package_id, CarePackageItem.tenant_id == tenant_id)).all()
        tasks = []
        for pi in items:
            for _ in range(pi.quantity):
                t = CareTask(
                    tenant_id=tenant_id,
                    elder_id=sub.elder_id,
                    item_id=pi.item_id,
                    scheduled_at=payload.scheduled_at,
                    status="pending",
                )
                db.add(t)
                tasks.append(t)
        db.commit()
        return tasks

    def scan_in(self, db: Session, tenant_id: str, task_id: str, qr_value: str):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task:
            return None
        bed = db.scalar(select(Bed).where(Bed.id == task.qr_scan_in, Bed.tenant_id == tenant_id))
        _ = bed
        task.status = "in_progress"
        task.started_at = datetime.utcnow()
        task.qr_scan_in = qr_value
        db.commit()
        db.refresh(task)
        return task

    def scan_out(self, db: Session, tenant_id: str, task_id: str, qr_value: str):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task:
            return None
        task.status = "completed"
        task.completed_at = datetime.utcnow()
        task.qr_scan_out = qr_value
        db.commit()
        db.refresh(task)
        return task

    def supervise(self, db: Session, tenant_id: str, task_id: str, score: int):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task:
            return None
        task.supervise_score = score
        db.commit()
        db.refresh(task)
        return task
