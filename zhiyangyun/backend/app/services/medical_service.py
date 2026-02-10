from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

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
    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_medication_orders(self, db: Session, tenant_id: str):
        return db.scalars(select(MedicationOrder).where(MedicationOrder.tenant_id == tenant_id)).all()

    def create_medication_order(self, db: Session, tenant_id: str, payload: MedicationOrderCreate):
        return self._save(db, MedicationOrder(tenant_id=tenant_id, **payload.model_dump()))

    def list_medication_executions(self, db: Session, tenant_id: str):
        return db.scalars(select(MedicationExecution).where(MedicationExecution.tenant_id == tenant_id)).all()

    def create_medication_execution(self, db: Session, tenant_id: str, payload: MedicationExecutionCreate, user_id: str):
        return self._save(db, MedicationExecution(tenant_id=tenant_id, executor_id=user_id, executed_at=datetime.utcnow(), **payload.model_dump()))

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
