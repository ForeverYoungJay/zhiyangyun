import json
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.care import (
    ServiceItem,
    CarePackage,
    CarePackageItem,
    ElderPackage,
    CareTask,
    CarePackageAssignment,
    CaregiverPerformance,
    TaskDispatchLog,
)
from app.models.elder import Elder
from app.models.user import User
from app.models.medical import BillingItem, BillingInvoice
from app.models.business import FamilyCareRecord
from app.models.rbac import Role, UserRole
from app.schemas.care import (
    ServiceItemCreate,
    CarePackageCreate,
    CarePackageItemCreate,
    ElderPackageCreate,
    CarePackageAssignmentCreate,
    TaskGenerateRequest,
    RoundTaskCreate,
    DispatchTasksRequest,
)


class CareService:
    def _role_codes(self, db: Session, tenant_id: str, user_id: str) -> set[str]:
        rows = db.execute(
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, UserRole.tenant_id == tenant_id, Role.tenant_id == tenant_id)
        ).all()
        return {r[0] for r in rows}

    def _ensure_roles(self, db: Session, tenant_id: str, user_id: str, allowed: set[str]) -> bool:
        roles = self._role_codes(db, tenant_id, user_id)
        return bool(roles.intersection(allowed) or "admin" in roles)

    def _next_by_frequency(self, at: datetime, frequency: str, i: int) -> datetime:
        if frequency == "day":
            return at + timedelta(days=i)
        if frequency == "month":
            return at + timedelta(days=30 * i)
        if frequency == "quarter":
            return at + timedelta(days=90 * i)
        if frequency == "year":
            return at + timedelta(days=365 * i)
        return at

    def _get_or_init_perf(self, db: Session, tenant_id: str, caregiver_id: str) -> CaregiverPerformance:
        perf = db.scalar(select(CaregiverPerformance).where(CaregiverPerformance.tenant_id == tenant_id, CaregiverPerformance.caregiver_id == caregiver_id))
        if not perf:
            perf = CaregiverPerformance(tenant_id=tenant_id, caregiver_id=caregiver_id, score=100)
            db.add(perf)
            db.flush()
        return perf

    def list_items(self, db: Session, tenant_id: str):
        return db.scalars(select(ServiceItem).where(ServiceItem.tenant_id == tenant_id)).all()

    def create_item(self, db: Session, tenant_id: str, payload: ServiceItemCreate):
        item = ServiceItem(
            tenant_id=tenant_id,
            name=payload.name,
            category=payload.category,
            unit_price=payload.unit_price,
            duration_min=payload.duration_min,
            status="active",
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_item_status(self, db: Session, tenant_id: str, item_id: str, status: str):
        item = db.scalar(select(ServiceItem).where(ServiceItem.id == item_id, ServiceItem.tenant_id == tenant_id))
        if not item:
            return None
        item.status = status
        db.commit()
        db.refresh(item)
        return item

    def delete_item(self, db: Session, tenant_id: str, item_id: str):
        item = db.scalar(select(ServiceItem).where(ServiceItem.id == item_id, ServiceItem.tenant_id == tenant_id))
        if not item:
            return False
        db.delete(item)
        db.commit()
        return True

    def list_packages(self, db: Session, tenant_id: str):
        return db.scalars(select(CarePackage).where(CarePackage.tenant_id == tenant_id)).all()

    def create_package(self, db: Session, tenant_id: str, payload: CarePackageCreate):
        item = CarePackage(tenant_id=tenant_id, name=payload.name, period=payload.period, default_months=payload.default_months)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update_package_status(self, db: Session, tenant_id: str, package_id: str, status: str):
        row = db.scalar(select(CarePackage).where(CarePackage.id == package_id, CarePackage.tenant_id == tenant_id))
        if not row:
            return None
        row.status = status
        db.commit()
        db.refresh(row)
        return row

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

    def assign_package_to_caregiver(self, db: Session, tenant_id: str, payload: CarePackageAssignmentCreate):
        end_date = payload.start_date + timedelta(days=30 * payload.months)
        row = CarePackageAssignment(
            tenant_id=tenant_id,
            package_id=payload.package_id,
            caregiver_id=payload.caregiver_id,
            start_date=payload.start_date,
            end_date=end_date,
            months=payload.months,
            status="active",
        )
        db.add(row)
        self._get_or_init_perf(db, tenant_id, payload.caregiver_id)
        db.commit()
        db.refresh(row)
        return row

    def list_assignments(self, db: Session, tenant_id: str):
        return db.scalars(select(CarePackageAssignment).where(CarePackageAssignment.tenant_id == tenant_id)).all()

    def list_caregivers(self, db: Session, tenant_id: str):
        return db.scalars(select(User).where(User.tenant_id == tenant_id, User.is_active == True)).all()

    def list_tasks(self, db: Session, tenant_id: str):
        return db.scalars(select(CareTask).where(CareTask.tenant_id == tenant_id).order_by(CareTask.scheduled_at.desc())).all()

    def task_board(self, db: Session, tenant_id: str):
        tasks = db.scalars(select(CareTask).where(CareTask.tenant_id == tenant_id, CareTask.status == "in_progress")).all()
        return [
            {
                "task_id": t.id,
                "assigned_to": t.assigned_to,
                "task_type": t.task_type,
                "started_at": t.started_at,
                "elapsed_seconds": int((datetime.utcnow() - t.started_at).total_seconds()) if t.started_at else 0,
            }
            for t in tasks
        ]

    def generate_tasks(self, db: Session, tenant_id: str, payload: TaskGenerateRequest):
        sub = db.scalar(select(ElderPackage).where(ElderPackage.id == payload.elder_package_id, ElderPackage.tenant_id == tenant_id))
        if not sub:
            return []
        assignments = db.scalars(select(CarePackageAssignment).where(CarePackageAssignment.package_id == sub.package_id, CarePackageAssignment.tenant_id == tenant_id, CarePackageAssignment.status == "active")).all()
        items = db.scalars(select(CarePackageItem).where(CarePackageItem.package_id == sub.package_id, CarePackageItem.tenant_id == tenant_id)).all()
        tasks = []
        for pi in items:
            for _ in range(pi.quantity):
                assigned_to = assignments[0].caregiver_id if assignments else None
                assignment_id = assignments[0].id if assignments else None
                t = CareTask(
                    tenant_id=tenant_id,
                    elder_id=sub.elder_id,
                    item_id=pi.item_id,
                    package_assignment_id=assignment_id,
                    assigned_to=assigned_to,
                    task_type="care",
                    scheduled_at=payload.scheduled_at,
                    status="pending",
                )
                db.add(t)
                tasks.append(t)
        db.commit()
        for t in tasks:
            db.refresh(t)
        return tasks

    def dispatch_tasks(self, db: Session, tenant_id: str, user_id: str, payload: DispatchTasksRequest):
        if not self._ensure_roles(db, tenant_id, user_id, {"nursing_director", "nursing_manager"}):
            return {"error": "无权限下发任务"}

        count = payload.custom_times if payload.frequency == "custom" else 1
        if payload.dispatch_type == "emergency":
            count = 1
        sub = db.scalar(select(ElderPackage).where(ElderPackage.id == payload.elder_package_id, ElderPackage.tenant_id == tenant_id))
        if not sub:
            return {"error": "未找到长者套餐订阅"}
        assignments = db.scalars(select(CarePackageAssignment).where(CarePackageAssignment.package_id == sub.package_id, CarePackageAssignment.tenant_id == tenant_id, CarePackageAssignment.status == "active")).all()
        items = db.scalars(select(CarePackageItem).where(CarePackageItem.package_id == sub.package_id, CarePackageItem.tenant_id == tenant_id)).all()
        created = []
        for i in range(count):
            when = payload.start_at if payload.frequency == "custom" else self._next_by_frequency(payload.start_at, payload.frequency, i)
            for pi in items:
                t = CareTask(
                    tenant_id=tenant_id,
                    elder_id=sub.elder_id,
                    item_id=pi.item_id,
                    package_assignment_id=assignments[0].id if assignments else None,
                    assigned_to=assignments[0].caregiver_id if assignments else None,
                    task_type="emergency" if payload.dispatch_type == "emergency" else "care",
                    created_by=user_id,
                    scheduled_at=when,
                    status="pending",
                )
                db.add(t)
                created.append(t)
        log = TaskDispatchLog(
            tenant_id=tenant_id,
            dispatcher_id=user_id,
            dispatch_type=payload.dispatch_type,
            frequency=payload.frequency,
            custom_times=count,
            created_tasks=len(created),
        )
        db.add(log)
        db.commit()
        for t in created:
            db.refresh(t)
        return {"tasks": created, "log": log}

    def create_round_task(self, db: Session, tenant_id: str, user_id: str, payload: RoundTaskCreate):
        if not self._ensure_roles(db, tenant_id, user_id, {"nursing_minister", "life_admin", "admin"}):
            return None
        t = CareTask(
            tenant_id=tenant_id,
            elder_id=payload.elder_id,
            item_id=payload.item_id,
            assigned_to=payload.assigned_to,
            task_type=payload.round_type,
            created_by=user_id,
            scheduled_at=payload.scheduled_at,
            status="pending",
        )
        db.add(t)
        db.commit()
        db.refresh(t)
        return t

    def scan_in(self, db: Session, tenant_id: str, user_id: str, task_id: str, qr_value: str):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task or task.status != "pending":
            return None

        elder = db.scalar(select(Elder).where(Elder.id == task.elder_id, Elder.tenant_id == tenant_id))
        if not elder or not elder.bed_id:
            return None

        bed = db.scalar(select(Bed).where(Bed.id == elder.bed_id, Bed.tenant_id == tenant_id))
        if not bed or bed.qr_code != qr_value:
            return None

        task.status = "in_progress"
        task.started_at = datetime.utcnow().replace(microsecond=0)
        task.qr_scan_in = qr_value
        if not task.assigned_to:
            task.assigned_to = user_id
        db.commit()
        db.refresh(task)
        return task

    def scan_out(self, db: Session, tenant_id: str, task_id: str, qr_value: str):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task or task.status != "in_progress":
            return None

        elder = db.scalar(select(Elder).where(Elder.id == task.elder_id, Elder.tenant_id == tenant_id))
        bed = db.scalar(select(Bed).where(Bed.id == elder.bed_id, Bed.tenant_id == tenant_id)) if elder and elder.bed_id else None
        if not bed or bed.qr_code != qr_value:
            return None

        item = db.scalar(select(ServiceItem).where(ServiceItem.id == task.item_id, ServiceItem.tenant_id == tenant_id))
        if not item:
            return None

        task.status = "completed"
        task.completed_at = datetime.utcnow().replace(microsecond=0)
        task.qr_scan_out = qr_value
        if task.started_at:
            task.execution_seconds = max(0, int((task.completed_at - task.started_at).total_seconds()))

        billing = BillingItem(
            tenant_id=tenant_id,
            elder_id=task.elder_id,
            item_name=f"护理任务:{item.name}",
            amount=item.unit_price,
            charged_on=datetime.utcnow().date(),
            status="unpaid",
        )
        db.add(billing)

        period = datetime.utcnow().strftime("%Y-%m")
        invoice = db.scalar(select(BillingInvoice).where(BillingInvoice.tenant_id == tenant_id, BillingInvoice.elder_id == task.elder_id, BillingInvoice.period_month == period))
        if not invoice:
            invoice = BillingInvoice(tenant_id=tenant_id, elder_id=task.elder_id, period_month=period, total_amount=0, paid_amount=0, status="open")
            db.add(invoice)
        invoice.total_amount = float(invoice.total_amount) + float(item.unit_price)

        care_record = FamilyCareRecord(
            tenant_id=tenant_id,
            elder_id=task.elder_id,
            task_id=task.id,
            content=f"{item.name}已完成，耗时{task.execution_seconds}秒，自动扣费{float(item.unit_price):.2f}元",
        )
        db.add(care_record)

        db.commit()
        db.refresh(task)
        return task

    def supervise(self, db: Session, tenant_id: str, task_id: str, score: int):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task or task.status != "completed":
            return None
        task.supervise_score = score
        db.commit()
        db.refresh(task)
        return task

    def report_issue(self, db: Session, tenant_id: str, task_id: str, photo_urls: list[str], description: str, report_to_dean: bool):
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task:
            return None
        task.issue_photo_urls = json.dumps(photo_urls, ensure_ascii=False)
        task.issue_description = description
        task.report_to_dean = report_to_dean
        if report_to_dean:
            task.dean_review_status = "reported"
        db.commit()
        db.refresh(task)
        return task

    def dean_review(self, db: Session, tenant_id: str, user_id: str, task_id: str, approved: bool, note: str, deduction_score: int):
        if not self._ensure_roles(db, tenant_id, user_id, {"dean", "admin"}):
            return {"error": "无院长审核权限"}
        task = db.scalar(select(CareTask).where(CareTask.id == task_id, CareTask.tenant_id == tenant_id))
        if not task or not task.assigned_to:
            return None
        task.dean_review_status = "approved" if approved else "rejected"
        task.dean_review_note = note
        task.dean_deduction = deduction_score if approved else 0

        perf = self._get_or_init_perf(db, tenant_id, task.assigned_to)
        if approved and deduction_score > 0:
            perf.score = max(0, perf.score - deduction_score)
            perf.last_deduction_at = datetime.utcnow()
            if perf.score < 80:
                perf.rotation_suggestion = "建议下月调岗，并重新选择服务项目"

        db.commit()
        db.refresh(task)
        db.refresh(perf)
        return {"task": task, "performance": perf}

    def get_performance(self, db: Session, tenant_id: str, caregiver_id: str):
        return self._get_or_init_perf(db, tenant_id, caregiver_id)
