from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.business import MiniappServiceRequest, FamilyAccount, FamilyVisit, DashboardMetric, FamilyCareRecord, FamilySurvey
from app.models.care import CareTask, CarePackage, ElderPackage, ServiceItem
from app.models.commerce import AccountLedger, ShopOrder
from app.models.elder import Elder
from app.models.medical import BillingItem, VitalSignRecord
from app.schemas.business import MiniappServiceRequestCreate, FamilyAccountCreate, FamilyVisitCreate, DashboardMetricCreate, FamilySurveyCreate, FamilyServiceOrderCreate


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

    def list_family_orders(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.elder_id == elder_id).order_by(ShopOrder.created_at.desc())).all()

    def list_family_balance_changes(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(AccountLedger).where(AccountLedger.tenant_id == tenant_id, AccountLedger.elder_id == elder_id).order_by(AccountLedger.created_at.desc())).all()

    def list_surveys(self, db: Session, tenant_id: str, elder_id: str | None = None):
        stmt = select(FamilySurvey).where(FamilySurvey.tenant_id == tenant_id)
        if elder_id:
            stmt = stmt.where(FamilySurvey.elder_id == elder_id)
        return db.scalars(stmt.order_by(FamilySurvey.created_at.desc())).all()

    def create_survey(self, db: Session, tenant_id: str, payload: FamilySurveyCreate):
        return self._save(db, FamilySurvey(tenant_id=tenant_id, **payload.model_dump()))

    def get_family_elder_overview(self, db: Session, tenant_id: str, elder_id: str):
        elder = db.scalar(select(Elder).where(Elder.tenant_id == tenant_id, Elder.id == elder_id))
        if not elder:
            return None

        latest_vital = db.scalar(
            select(VitalSignRecord)
            .where(VitalSignRecord.tenant_id == tenant_id, VitalSignRecord.elder_id == elder_id)
            .order_by(VitalSignRecord.recorded_at.desc())
            .limit(1)
        )

        open_packages = db.scalar(
            select(func.count()).select_from(ElderPackage).where(
                ElderPackage.tenant_id == tenant_id,
                ElderPackage.elder_id == elder_id,
                ElderPackage.status == "active",
            )
        ) or 0

        return {
            "elder": elder,
            "latest_vital": latest_vital,
            "active_packages": int(open_packages),
        }

    def list_service_catalog(self, db: Session, tenant_id: str):
        return {
            "items": db.scalars(
                select(ServiceItem).where(ServiceItem.tenant_id == tenant_id, ServiceItem.status == "active")
            ).all(),
            "packages": db.scalars(
                select(CarePackage).where(CarePackage.tenant_id == tenant_id, CarePackage.status == "active")
            ).all(),
        }

    def create_family_service_order(self, db: Session, tenant_id: str, payload: FamilyServiceOrderCreate):
        row = ElderPackage(
            tenant_id=tenant_id,
            elder_id=payload.elder_id,
            package_id=payload.package_id,
            start_date=payload.start_date or date.today(),
            status="active",
        )
        return self._save(db, row)

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
