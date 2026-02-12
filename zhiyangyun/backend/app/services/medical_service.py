from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.models.elder import Elder
from app.models.medical import (
    MedicationOrder,
    MedicationExecution,
    MealPlan,
    MealOrder,
    VitalSignRecord,
    HealthAssessment,
    BillingItem,
    BillingInvoice,
)
from app.schemas.medical import (
    MedicationOrderCreate,
    MedicationExecutionCreate,
    MealPlanCreate,
    MealOrderCreate,
    VitalSignCreate,
    HealthAssessmentCreate,
    BillingItemCreate,
    BillingInvoiceCreate,
)


class MedicalService:
    MEDICATION_EXECUTION_FEE = Decimal("12.00")

    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def _to_plain(self, obj):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}

    def _pager(self, rows: list, page: int, page_size: int):
        total = len(rows)
        start = (page - 1) * page_size
        return {
            "items": rows[start:start + page_size],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def _resolve_elder(self, db: Session, tenant_id: str, elder_id: str):
        elder = db.scalar(select(Elder).where(Elder.tenant_id == tenant_id, Elder.id == elder_id))
        if not elder:
            raise ValueError("长者不存在")
        return elder

    def suggest_elders(self, db: Session, tenant_id: str, keyword: str = "", limit: int = 10):
        stmt = select(Elder).where(Elder.tenant_id == tenant_id)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(Elder.name.like(like_kw), Elder.elder_no.like(like_kw)))
        elders = db.scalars(stmt.order_by(Elder.name.asc()).limit(limit)).all()
        return [{"id": e.id, "name": e.name, "elder_no": e.elder_no, "status": e.status} for e in elders]

    def list_medication_orders(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
        elder_id: str = "",
    ):
        stmt = select(MedicationOrder, Elder.name.label("elder_name"), Elder.elder_no.label("elder_no")).join(
            Elder, Elder.id == MedicationOrder.elder_id
        ).where(MedicationOrder.tenant_id == tenant_id, Elder.tenant_id == tenant_id)

        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    MedicationOrder.drug_name.like(like_kw),
                    MedicationOrder.dosage.like(like_kw),
                    MedicationOrder.frequency.like(like_kw),
                    Elder.name.like(like_kw),
                    Elder.elder_no.like(like_kw),
                )
            )
        if status:
            stmt = stmt.where(MedicationOrder.status == status)
        if elder_id:
            stmt = stmt.where(MedicationOrder.elder_id == elder_id)

        rows = db.execute(stmt.order_by(MedicationOrder.start_date.desc(), MedicationOrder.id.desc())).all()
        payload = []
        for order, elder_name, elder_no in rows:
            payload.append({
                **self._to_plain(order),
                "elder_name": elder_name,
                "elder_no": elder_no,
            })
        return self._pager(payload, page, page_size)

    def create_medication_order(self, db: Session, tenant_id: str, payload: MedicationOrderCreate):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        if elder.status == "discharged":
            raise ValueError("该长者已退院，不能新建用药医嘱")
        obj = MedicationOrder(tenant_id=tenant_id, **payload.model_dump())
        saved = self._save(db, obj)
        return {**self._to_plain(saved), "elder_name": elder.name, "elder_no": elder.elder_no}

    def list_medication_executions(self, db: Session, tenant_id: str):
        stmt = (
            select(
                MedicationExecution,
                MedicationOrder.drug_name.label("drug_name"),
                Elder.name.label("elder_name"),
                Elder.elder_no.label("elder_no"),
            )
            .join(MedicationOrder, MedicationOrder.id == MedicationExecution.order_id)
            .join(Elder, Elder.id == MedicationOrder.elder_id)
            .where(MedicationExecution.tenant_id == tenant_id, MedicationOrder.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
            .order_by(MedicationExecution.executed_at.desc())
        )
        rows = db.execute(stmt).all()
        return [
            {
                **self._to_plain(execution),
                "drug_name": drug_name,
                "elder_name": elder_name,
                "elder_no": elder_no,
            }
            for execution, drug_name, elder_name, elder_no in rows
        ]

    def _upsert_invoice_total(self, db: Session, tenant_id: str, elder_id: str, charged_on: date, amount: Decimal):
        month = charged_on.strftime("%Y-%m")
        invoice = db.scalar(
            select(BillingInvoice).where(
                BillingInvoice.tenant_id == tenant_id,
                BillingInvoice.elder_id == elder_id,
                BillingInvoice.period_month == month,
            )
        )
        if not invoice:
            invoice = BillingInvoice(
                tenant_id=tenant_id,
                elder_id=elder_id,
                period_month=month,
                total_amount=amount,
                paid_amount=0,
                status="open",
            )
            db.add(invoice)
        else:
            invoice.total_amount = Decimal(str(invoice.total_amount)) + amount
        return invoice

    def create_medication_execution(self, db: Session, tenant_id: str, payload: MedicationExecutionCreate, user_id: str):
        order = db.scalar(
            select(MedicationOrder).where(MedicationOrder.tenant_id == tenant_id, MedicationOrder.id == payload.order_id)
        )
        if not order:
            raise ValueError("医嘱不存在")
        if order.status == "stopped":
            raise ValueError("医嘱已停用，不能执行")

        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        duplicate = db.scalar(
            select(MedicationExecution).where(
                MedicationExecution.tenant_id == tenant_id,
                MedicationExecution.order_id == payload.order_id,
                MedicationExecution.executed_at >= today_start,
            )
        )
        if duplicate:
            raise ValueError("该医嘱今日已执行，无需重复登记")

        execution = MedicationExecution(
            tenant_id=tenant_id,
            executor_id=user_id,
            executed_at=datetime.utcnow(),
            **payload.model_dump(),
        )
        db.add(execution)

        if payload.result == "done":
            charged_on = datetime.utcnow().date()
            db.add(
                BillingItem(
                    tenant_id=tenant_id,
                    elder_id=order.elder_id,
                    item_name=f"用药执行：{order.drug_name}",
                    amount=self.MEDICATION_EXECUTION_FEE,
                    charged_on=charged_on,
                    status="unpaid",
                )
            )
            self._upsert_invoice_total(db, tenant_id, order.elder_id, charged_on, self.MEDICATION_EXECUTION_FEE)

        latest_done = db.scalar(
            select(func.count(MedicationExecution.id)).where(
                MedicationExecution.tenant_id == tenant_id,
                MedicationExecution.order_id == payload.order_id,
                MedicationExecution.result == "done",
            )
        )
        order.status = "active" if (latest_done or 0) > 0 else order.status

        db.commit()
        db.refresh(execution)
        return execution

    def list_meal_plans(self, db: Session, tenant_id: str):
        return db.scalars(select(MealPlan).where(MealPlan.tenant_id == tenant_id)).all()

    def create_meal_plan(self, db: Session, tenant_id: str, payload: MealPlanCreate):
        return self._save(db, MealPlan(tenant_id=tenant_id, **payload.model_dump()))

    def list_meal_orders(self, db: Session, tenant_id: str):
        return db.scalars(select(MealOrder).where(MealOrder.tenant_id == tenant_id)).all()

    def create_meal_order(self, db: Session, tenant_id: str, payload: MealOrderCreate):
        return self._save(db, MealOrder(tenant_id=tenant_id, **payload.model_dump()))

    def list_vitals(self, db: Session, tenant_id: str):
        return db.scalars(select(VitalSignRecord).where(VitalSignRecord.tenant_id == tenant_id)).all()

    def create_vital(self, db: Session, tenant_id: str, payload: VitalSignCreate):
        return self._save(db, VitalSignRecord(tenant_id=tenant_id, **payload.model_dump()))

    def list_assessments(self, db: Session, tenant_id: str):
        return db.scalars(select(HealthAssessment).where(HealthAssessment.tenant_id == tenant_id)).all()

    def create_assessment(self, db: Session, tenant_id: str, payload: HealthAssessmentCreate):
        return self._save(db, HealthAssessment(tenant_id=tenant_id, **payload.model_dump()))

    def list_billing_items(self, db: Session, tenant_id: str):
        return db.scalars(select(BillingItem).where(BillingItem.tenant_id == tenant_id)).all()

    def create_billing_item(self, db: Session, tenant_id: str, payload: BillingItemCreate):
        return self._save(db, BillingItem(tenant_id=tenant_id, **payload.model_dump()))

    def list_invoices(self, db: Session, tenant_id: str):
        return db.scalars(select(BillingInvoice).where(BillingInvoice.tenant_id == tenant_id)).all()

    def create_invoice(self, db: Session, tenant_id: str, payload: BillingInvoiceCreate):
        body = payload.model_dump()
        body["paid_amount"] = 0
        return self._save(db, BillingInvoice(tenant_id=tenant_id, **body))
