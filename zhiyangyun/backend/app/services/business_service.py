from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.business import MiniappServiceRequest, FamilyAccount, FamilyVisit, DashboardMetric
from app.schemas.business import MiniappServiceRequestCreate, FamilyAccountCreate, FamilyVisitCreate, DashboardMetricCreate


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
