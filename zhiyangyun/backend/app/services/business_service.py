from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.business import MiniappServiceRequest, FamilyAccount, FamilyVisit, DashboardMetric, FamilyCareRecord, FamilySurvey
from app.models.care import CareTask
from app.models.medical import BillingItem
from app.schemas.business import MiniappServiceRequestCreate, FamilyAccountCreate, FamilyVisitCreate, DashboardMetricCreate, FamilySurveyCreate


class BusinessService:
    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_requests(self, db: Session, tenant_id: str):
        return db.scalars(select(MiniappServiceRequest).where(MiniappServiceRequest.tenant_id == tenant_id)).all()

    def create_request(self, db: Session, tenant_id: str, payload: MiniappServiceRequestCreate):
        return self._save(db, MiniappServiceRequest(tenant_id=tenant_id, **payload.model_dump()))

    def list_families(self, db: Session, tenant_id: str):
        return db.scalars(select(FamilyAccount).where(FamilyAccount.tenant_id == tenant_id)).all()

    def create_family(self, db: Session, tenant_id: str, payload: FamilyAccountCreate):
        return self._save(db, FamilyAccount(tenant_id=tenant_id, **payload.model_dump()))

    def list_visits(self, db: Session, tenant_id: str):
        return db.scalars(select(FamilyVisit).where(FamilyVisit.tenant_id == tenant_id)).all()

    def create_visit(self, db: Session, tenant_id: str, payload: FamilyVisitCreate):
        return self._save(db, FamilyVisit(tenant_id=tenant_id, **payload.model_dump()))

    def list_metrics(self, db: Session, tenant_id: str):
        return db.scalars(select(DashboardMetric).where(DashboardMetric.tenant_id == tenant_id)).all()

    def create_metric(self, db: Session, tenant_id: str, payload: DashboardMetricCreate):
        return self._save(db, DashboardMetric(tenant_id=tenant_id, **payload.model_dump()))

    def list_family_bills(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(BillingItem).where(BillingItem.tenant_id == tenant_id, BillingItem.elder_id == elder_id).order_by(BillingItem.charged_on.desc())).all()

    def list_family_care_records(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(FamilyCareRecord).where(FamilyCareRecord.tenant_id == tenant_id, FamilyCareRecord.elder_id == elder_id).order_by(FamilyCareRecord.occurred_at.desc())).all()

    def list_surveys(self, db: Session, tenant_id: str, elder_id: str | None = None):
        stmt = select(FamilySurvey).where(FamilySurvey.tenant_id == tenant_id)
        if elder_id:
            stmt = stmt.where(FamilySurvey.elder_id == elder_id)
        return db.scalars(stmt.order_by(FamilySurvey.created_at.desc())).all()

    def create_survey(self, db: Session, tenant_id: str, payload: FamilySurveyCreate):
        return self._save(db, FamilySurvey(tenant_id=tenant_id, **payload.model_dump()))

    def get_performance_summary(self, db: Session, tenant_id: str):
        today = date.today()
        completed = db.scalar(select(func.count()).select_from(CareTask).where(CareTask.tenant_id == tenant_id, CareTask.status == "completed")) or 0
        avg_score = db.scalar(select(func.avg(CareTask.supervise_score)).where(CareTask.tenant_id == tenant_id, CareTask.status == "completed")) or 0
        survey_avg = db.scalar(select(func.avg(FamilySurvey.score)).where(FamilySurvey.tenant_id == tenant_id)) or 0
        revenue = db.scalar(select(func.coalesce(func.sum(BillingItem.amount), 0)).where(BillingItem.tenant_id == tenant_id, BillingItem.charged_on == today)) or 0
        total_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.tenant_id == tenant_id)) or 0
        occupied_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.tenant_id == tenant_id, Bed.status == "occupied")) or 0

        return {
            "date": str(today),
            "completed_tasks": int(completed),
            "avg_supervise_score": round(float(avg_score), 2),
            "survey_avg": round(float(survey_avg), 2),
            "today_revenue": round(float(revenue), 2),
            "occupancy_rate": round((occupied_beds / total_beds) * 100, 2) if total_beds else 0,
        }
