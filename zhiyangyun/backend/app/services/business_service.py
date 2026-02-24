from datetime import date

from sqlalchemy import func, select, or_
from sqlalchemy.orm import Session

from app.models.asset import Bed
from app.models.business import MiniappServiceRequest, FamilyAccount, FamilyVisit, DashboardMetric, FamilyCareRecord, FamilySurvey
from app.models.care import CareTask, CarePackage, ElderPackage, ServiceItem
from app.models.commerce import AccountLedger, ShopOrder
from app.models.elder import Elder
from app.models.medical import BillingItem, VitalSignRecord
from app.models.oa import NotificationMessage
from app.schemas.business import MiniappServiceRequestCreate, FamilyAccountCreate, FamilyVisitCreate, DashboardMetricCreate, FamilySurveyCreate, FamilyServiceOrderCreate


class BusinessService:
    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def _pager(self, rows: list, page: int, page_size: int):
        total = len(rows)
        start = (page - 1) * page_size
        return {"items": rows[start:start + page_size], "total": total, "page": page, "page_size": page_size}

    def list_requests(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", elder_id: str = ""):
        stmt = (
            select(MiniappServiceRequest, Elder.name, Elder.elder_no)
            .join(Elder, Elder.id == MiniappServiceRequest.elder_id)
            .where(MiniappServiceRequest.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
            .order_by(MiniappServiceRequest.id.desc())
        )
        if elder_id:
            stmt = stmt.where(MiniappServiceRequest.elder_id == elder_id)
        if status:
            stmt = stmt.where(MiniappServiceRequest.status == status)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    MiniappServiceRequest.content.ilike(like_kw),
                    MiniappServiceRequest.request_type.ilike(like_kw),
                    Elder.name.ilike(like_kw),
                    Elder.elder_no.ilike(like_kw),
                )
            )
        rows = db.execute(stmt).all()
        payload = [{**r[0].to_dict(), "elder_name": r[1], "elder_no": r[2]} for r in rows]
        return self._pager(payload, page, page_size)

    def create_request(self, db: Session, tenant_id: str, payload: MiniappServiceRequestCreate):
        row = self._save(db, MiniappServiceRequest(tenant_id=tenant_id, **payload.model_dump()))
        db.add(
            NotificationMessage(
                tenant_id=tenant_id,
                title="小程序服务请求",
                content=f"长者服务请求已提交：{payload.request_type} / {payload.content}",
                channel="in_app",
                receiver_scope="caregiver",
            )
        )
        db.commit()
        return row

    def update_request_status(self, db: Session, tenant_id: str, request_id: str, status: str):
        obj = db.scalar(select(MiniappServiceRequest).where(MiniappServiceRequest.tenant_id == tenant_id, MiniappServiceRequest.id == request_id))
        if not obj:
            raise ValueError("服务请求不存在")
        obj.status = status
        db.add(NotificationMessage(tenant_id=tenant_id, title="服务请求状态更新", content=f"请求状态已更新为：{status}", channel="in_app", receiver_scope="family"))
        db.commit()
        db.refresh(obj)
        return obj

    def list_families(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", relation: str = "", elder_id: str = ""):
        stmt = (
            select(FamilyAccount, Elder.name, Elder.elder_no)
            .join(Elder, Elder.id == FamilyAccount.elder_id)
            .where(FamilyAccount.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
            .order_by(FamilyAccount.id.desc())
        )
        if relation:
            stmt = stmt.where(FamilyAccount.relation == relation)
        if elder_id:
            stmt = stmt.where(FamilyAccount.elder_id == elder_id)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(FamilyAccount.name.ilike(like_kw), FamilyAccount.phone.ilike(like_kw), Elder.name.ilike(like_kw), Elder.elder_no.ilike(like_kw)))
        rows = db.execute(stmt).all()
        payload = [{**r[0].to_dict(), "elder_name": r[1], "elder_no": r[2]} for r in rows]
        return self._pager(payload, page, page_size)

    def create_family(self, db: Session, tenant_id: str, payload: FamilyAccountCreate):
        return self._save(db, FamilyAccount(tenant_id=tenant_id, **payload.model_dump()))

    def list_visits(self, db: Session, tenant_id: str):
        return db.scalars(select(FamilyVisit).where(FamilyVisit.tenant_id == tenant_id)).all()

    def create_visit(self, db: Session, tenant_id: str, payload: FamilyVisitCreate):
        row = self._save(db, FamilyVisit(tenant_id=tenant_id, **payload.model_dump()))
        db.add(NotificationMessage(tenant_id=tenant_id, title="家属探访预约", content=f"探访日期：{payload.visit_date}", channel="in_app", receiver_scope="caregiver"))
        db.commit()
        return row

    def list_metrics(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, start_date: str = "", end_date: str = ""):
        stmt = select(DashboardMetric).where(DashboardMetric.tenant_id == tenant_id).order_by(DashboardMetric.metric_date.desc())
        if start_date:
            stmt = stmt.where(DashboardMetric.metric_date >= start_date)
        if end_date:
            stmt = stmt.where(DashboardMetric.metric_date <= end_date)
        rows = [x.to_dict() for x in db.scalars(stmt).all()]
        return self._pager(rows, page, page_size)

    def create_metric(self, db: Session, tenant_id: str, payload: DashboardMetricCreate):
        return self._save(db, DashboardMetric(tenant_id=tenant_id, **payload.model_dump()))

    def list_family_bills(self, db: Session, tenant_id: str, elder_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = ""):
        stmt = select(BillingItem).where(BillingItem.tenant_id == tenant_id, BillingItem.elder_id == elder_id).order_by(BillingItem.charged_on.desc())
        if status:
            stmt = stmt.where(BillingItem.status == status)
        if keyword:
            stmt = stmt.where(BillingItem.item_name.ilike(f"%{keyword.strip()}%"))
        return self._pager([x.to_dict() for x in db.scalars(stmt).all()], page, page_size)

    def list_family_care_records(self, db: Session, tenant_id: str, elder_id: str, page: int = 1, page_size: int = 10, keyword: str = ""):
        stmt = select(FamilyCareRecord).where(FamilyCareRecord.tenant_id == tenant_id, FamilyCareRecord.elder_id == elder_id).order_by(FamilyCareRecord.occurred_at.desc())
        if keyword:
            stmt = stmt.where(FamilyCareRecord.content.ilike(f"%{keyword.strip()}%"))
        return self._pager([x.to_dict() for x in db.scalars(stmt).all()], page, page_size)

    def list_family_orders(self, db: Session, tenant_id: str, elder_id: str, page: int = 1, page_size: int = 10, status: str = ""):
        stmt = select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.elder_id == elder_id).order_by(ShopOrder.created_at.desc())
        if status:
            stmt = stmt.where(ShopOrder.status == status)
        return self._pager([x.to_dict() for x in db.scalars(stmt).all()], page, page_size)

    def list_family_balance_changes(self, db: Session, tenant_id: str, elder_id: str, page: int = 1, page_size: int = 10):
        stmt = select(AccountLedger).where(AccountLedger.tenant_id == tenant_id, AccountLedger.elder_id == elder_id).order_by(AccountLedger.created_at.desc())
        return self._pager([x.to_dict() for x in db.scalars(stmt).all()], page, page_size)

    def list_surveys(self, db: Session, tenant_id: str, elder_id: str | None = None, page: int = 1, page_size: int = 10):
        stmt = select(FamilySurvey).where(FamilySurvey.tenant_id == tenant_id)
        if elder_id:
            stmt = stmt.where(FamilySurvey.elder_id == elder_id)
        return self._pager([x.to_dict() for x in db.scalars(stmt.order_by(FamilySurvey.created_at.desc())).all()], page, page_size)

    def create_survey(self, db: Session, tenant_id: str, payload: FamilySurveyCreate):
        row = self._save(db, FamilySurvey(tenant_id=tenant_id, **payload.model_dump()))
        db.add(NotificationMessage(tenant_id=tenant_id, title="家属评价反馈", content=f"评分：{payload.score}；评价：{payload.comment or '无'}", channel="in_app", receiver_scope="caregiver"))
        db.commit()
        return row

    def list_family_notifications(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = ""):
        stmt = select(NotificationMessage).where(NotificationMessage.tenant_id == tenant_id, NotificationMessage.receiver_scope.in_(["all", "family"]))
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(NotificationMessage.title.ilike(like_kw), NotificationMessage.content.ilike(like_kw)))
        rows = [x.to_dict() for x in db.scalars(stmt.order_by(NotificationMessage.sent_at.desc())).all()]
        return self._pager(rows, page, page_size)

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
        saved = self._save(db, row)
        db.add(NotificationMessage(tenant_id=tenant_id, title="家属服务增购", content=f"长者 {payload.elder_id} 增购套餐 {payload.package_id}", channel="in_app", receiver_scope="caregiver"))
        db.commit()
        return saved

    def get_performance_summary(self, db: Session, tenant_id: str):
        today = date.today()
        completed = db.scalar(select(func.count()).select_from(CareTask).where(CareTask.tenant_id == tenant_id, CareTask.status == "completed")) or 0
        avg_score = db.scalar(select(func.avg(CareTask.supervise_score)).where(CareTask.tenant_id == tenant_id, CareTask.status == "completed")) or 0
        survey_avg = db.scalar(select(func.avg(FamilySurvey.score)).where(FamilySurvey.tenant_id == tenant_id)) or 0
        realtime_revenue = db.scalar(select(func.coalesce(func.sum(BillingItem.amount), 0)).where(BillingItem.tenant_id == tenant_id, BillingItem.charged_on == today)) or 0
        total_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.tenant_id == tenant_id)) or 0
        occupied_beds = db.scalar(select(func.count()).select_from(Bed).where(Bed.tenant_id == tenant_id, Bed.status == "occupied")) or 0

        latest_metric = db.scalar(select(DashboardMetric).where(DashboardMetric.tenant_id == tenant_id).order_by(DashboardMetric.metric_date.desc()).limit(1))
        manual_occupancy = float(getattr(latest_metric, "occupancy_rate", 0) or 0)
        manual_revenue = float(getattr(latest_metric, "revenue", 0) or 0)
        manual_alerts = int(getattr(latest_metric, "alerts", 0) or 0)

        occupancy_rate = round((occupied_beds / total_beds) * 100, 2) if total_beds else 0
        if latest_metric and str(latest_metric.metric_date) == str(today):
            occupancy_rate = max(occupancy_rate, manual_occupancy)

        return {
            "date": str(today),
            "completed_tasks": int(completed),
            "avg_supervise_score": round(float(avg_score), 2),
            "survey_avg": round(float(survey_avg), 2),
            "today_revenue": round(max(float(realtime_revenue), manual_revenue if latest_metric and str(latest_metric.metric_date) == str(today) else 0), 2),
            "occupancy_rate": occupancy_rate,
            "alerts": manual_alerts,
            "manual_metric_date": str(latest_metric.metric_date) if latest_metric else None,
            "manual_revenue": round(manual_revenue, 2),
            "manual_occupancy_rate": round(manual_occupancy, 2),
        }
