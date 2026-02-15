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
from app.models.care import CareTask, ServiceItem
from app.models.oa import ApprovalRequest, NotificationMessage
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

    def list_meal_plans(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        meal_type: str = "",
    ):
        stmt = select(MealPlan).where(MealPlan.tenant_id == tenant_id)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(MealPlan.name.like(like_kw), MealPlan.nutrition_tag.like(like_kw), MealPlan.note.like(like_kw)))
        if meal_type:
            stmt = stmt.where(MealPlan.meal_type == meal_type)
        rows = db.scalars(stmt.order_by(MealPlan.plan_date.desc(), MealPlan.id.desc())).all()
        return self._pager([self._to_plain(x) for x in rows], page, page_size)

    def create_meal_plan(self, db: Session, tenant_id: str, payload: MealPlanCreate):
        return self._save(db, MealPlan(tenant_id=tenant_id, **payload.model_dump()))

    def list_meal_orders(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
    ):
        stmt = (
            select(
                MealOrder,
                Elder.name.label("elder_name"),
                Elder.elder_no.label("elder_no"),
                MealPlan.name.label("plan_name"),
                MealPlan.meal_type.label("meal_type"),
                MealPlan.nutrition_tag.label("nutrition_tag"),
            )
            .join(Elder, Elder.id == MealOrder.elder_id)
            .join(MealPlan, MealPlan.id == MealOrder.plan_id)
            .where(MealOrder.tenant_id == tenant_id, Elder.tenant_id == tenant_id, MealPlan.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(Elder.name.like(like_kw), Elder.elder_no.like(like_kw), MealPlan.name.like(like_kw), MealPlan.nutrition_tag.like(like_kw)))
        if status:
            stmt = stmt.where(MealOrder.status == status)
        rows = db.execute(stmt.order_by(MealOrder.id.desc())).all()
        payload = [
            {
                **self._to_plain(order),
                "elder_name": elder_name,
                "elder_no": elder_no,
                "plan_name": plan_name,
                "meal_type": meal_type,
                "nutrition_tag": nutrition_tag,
            }
            for order, elder_name, elder_no, plan_name, meal_type, nutrition_tag in rows
        ]
        return self._pager(payload, page, page_size)

    def create_meal_order(self, db: Session, tenant_id: str, payload: MealOrderCreate):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        if elder.status != "admitted":
            raise ValueError("仅在院长者可下发膳食订单")

        plan = db.scalar(select(MealPlan).where(MealPlan.tenant_id == tenant_id, MealPlan.id == payload.plan_id))
        if not plan:
            raise ValueError("膳食方案不存在")

        today_order = db.scalar(
            select(MealOrder)
            .join(MealPlan, MealPlan.id == MealOrder.plan_id)
            .where(
                MealOrder.tenant_id == tenant_id,
                MealOrder.elder_id == payload.elder_id,
                MealPlan.plan_date == plan.plan_date,
                MealPlan.meal_type == plan.meal_type,
            )
        )
        if today_order:
            raise ValueError("该长者同餐次膳食已下发，请勿重复")

        order = MealOrder(tenant_id=tenant_id, **payload.model_dump())
        db.add(order)

        meal_fee = Decimal("18.00")
        db.add(
            BillingItem(
                tenant_id=tenant_id,
                elder_id=payload.elder_id,
                item_name=f"膳食供应：{plan.name}",
                amount=meal_fee,
                charged_on=plan.plan_date,
                status="unpaid",
            )
        )
        self._upsert_invoice_total(db, tenant_id, payload.elder_id, plan.plan_date, meal_fee)

        db.commit()
        db.refresh(order)
        return {
            **self._to_plain(order),
            "elder_name": elder.name,
            "elder_no": elder.elder_no,
            "plan_name": plan.name,
            "meal_type": plan.meal_type,
            "nutrition_tag": plan.nutrition_tag,
        }

    def _ensure_followup_item(self, db: Session, tenant_id: str):
        item = db.scalar(select(ServiceItem).where(ServiceItem.tenant_id == tenant_id, ServiceItem.name == "健康随访"))
        if item:
            return item
        item = ServiceItem(tenant_id=tenant_id, name="健康随访", category="care", unit_price=0, duration_min=30, status="active")
        db.add(item)
        db.flush()
        return item

    def _create_health_followup_task(self, db: Session, tenant_id: str, elder_id: str, user_id: str, description: str):
        item = self._ensure_followup_item(db, tenant_id)
        task = CareTask(
            tenant_id=tenant_id,
            elder_id=elder_id,
            item_id=item.id,
            task_type="health_followup",
            created_by=user_id,
            assigned_to=user_id,
            scheduled_at=datetime.utcnow(),
            status="pending",
            issue_description=description,
            report_to_dean=True,
        )
        db.add(task)
        db.flush()
        return task

    def _create_health_alert(self, db: Session, tenant_id: str, title: str, content: str, biz_id: str, user_id: str):
        db.add(NotificationMessage(tenant_id=tenant_id, title=title, content=content, channel="in_app", receiver_scope="all"))
        db.add(ApprovalRequest(tenant_id=tenant_id, module="m6-health", biz_id=biz_id, applicant_id=user_id, note=content, status="pending"))

    def _vital_abnormal_rule(self, payload: VitalSignCreate):
        reasons = []
        level = "normal"
        if payload.temperature >= 38.5 or payload.temperature <= 35.5:
            reasons.append(f"体温异常({payload.temperature}℃)")
            level = "critical"
        elif payload.temperature >= 37.3:
            reasons.append(f"体温偏高({payload.temperature}℃)")
            level = "warning"

        if payload.systolic >= 180 or payload.diastolic >= 110 or payload.systolic <= 90:
            reasons.append(f"血压异常({payload.systolic}/{payload.diastolic}mmHg)")
            level = "critical"
        elif payload.systolic >= 140 or payload.diastolic >= 90:
            reasons.append(f"血压偏高({payload.systolic}/{payload.diastolic}mmHg)")
            level = "warning" if level == "normal" else level

        if payload.pulse >= 120 or payload.pulse <= 50:
            reasons.append(f"脉搏异常({payload.pulse}次/分)")
            level = "critical" if (payload.pulse >= 130 or payload.pulse <= 45) else ("warning" if level == "normal" else level)

        return level, "；".join(reasons)

    def list_vitals(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        abnormal_level: str = "",
    ):
        stmt = (
            select(VitalSignRecord, Elder.name.label("elder_name"), Elder.elder_no.label("elder_no"))
            .join(Elder, Elder.id == VitalSignRecord.elder_id)
            .where(VitalSignRecord.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(Elder.name.like(like_kw), Elder.elder_no.like(like_kw), VitalSignRecord.abnormal_reason.like(like_kw)))
        if abnormal_level:
            stmt = stmt.where(VitalSignRecord.abnormal_level == abnormal_level)

        rows = db.execute(stmt.order_by(VitalSignRecord.recorded_at.desc(), VitalSignRecord.id.desc())).all()
        payload = []
        for vital, elder_name, elder_no in rows:
            payload.append({**self._to_plain(vital), "elder_name": elder_name, "elder_no": elder_no})
        return self._pager(payload, page, page_size)

    def create_vital(self, db: Session, tenant_id: str, payload: VitalSignCreate, user_id: str):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        abnormal_level, abnormal_reason = self._vital_abnormal_rule(payload)
        vital = VitalSignRecord(
            tenant_id=tenant_id,
            **payload.model_dump(),
            abnormal_level=abnormal_level,
            abnormal_reason=abnormal_reason,
        )
        db.add(vital)
        db.flush()

        if abnormal_level in ["warning", "critical"]:
            followup = self._create_health_followup_task(
                db,
                tenant_id,
                payload.elder_id,
                user_id,
                f"生命体征{abnormal_level}：{abnormal_reason}",
            )
            vital.followup_task_id = followup.id
            self._create_health_alert(
                db,
                tenant_id,
                title=f"生命体征{abnormal_level}告警：{elder.name}",
                content=f"{elder.name}({elder.elder_no}) {abnormal_reason}，已自动生成随访任务。",
                biz_id=vital.id,
                user_id=user_id,
            )

        db.commit()
        db.refresh(vital)
        return {**self._to_plain(vital), "elder_name": elder.name, "elder_no": elder.elder_no}

    def list_assessments(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
    ):
        stmt = (
            select(HealthAssessment, Elder.name.label("elder_name"), Elder.elder_no.label("elder_no"))
            .join(Elder, Elder.id == HealthAssessment.elder_id)
            .where(HealthAssessment.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(Elder.name.like(like_kw), Elder.elder_no.like(like_kw), HealthAssessment.risk_level.like(like_kw), HealthAssessment.close_note.like(like_kw)))
        if status:
            stmt = stmt.where(HealthAssessment.status == status)
        rows = db.execute(stmt.order_by(HealthAssessment.assessed_on.desc(), HealthAssessment.id.desc())).all()
        payload = []
        for assessment, elder_name, elder_no in rows:
            payload.append({**self._to_plain(assessment), "elder_name": elder_name, "elder_no": elder_no})
        return self._pager(payload, page, page_size)

    def create_assessment(self, db: Session, tenant_id: str, payload: HealthAssessmentCreate, user_id: str):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        assessment = HealthAssessment(tenant_id=tenant_id, **payload.model_dump(), status="open")
        db.add(assessment)
        db.flush()

        need_followup = payload.risk_level in ["high", "critical"] or payload.adl_score < 40 or payload.mmse_score < 18
        if need_followup:
            task = self._create_health_followup_task(
                db,
                tenant_id,
                payload.elder_id,
                user_id,
                f"健康评估高风险：risk={payload.risk_level}, ADL={payload.adl_score}, MMSE={payload.mmse_score}",
            )
            assessment.followup_task_id = task.id
            self._create_health_alert(
                db,
                tenant_id,
                title=f"健康评估高风险：{elder.name}",
                content=f"{elder.name}({elder.elder_no})评估风险{payload.risk_level}，已自动生成闭环随访任务。",
                biz_id=assessment.id,
                user_id=user_id,
            )

        db.commit()
        db.refresh(assessment)
        return {**self._to_plain(assessment), "elder_name": elder.name, "elder_no": elder.elder_no}

    def close_assessment(self, db: Session, tenant_id: str, assessment_id: str, note: str = ""):
        obj = db.scalar(select(HealthAssessment).where(HealthAssessment.tenant_id == tenant_id, HealthAssessment.id == assessment_id))
        if not obj:
            raise ValueError("评估记录不存在")
        obj.status = "closed"
        obj.closed_at = datetime.utcnow()
        obj.close_note = note
        db.commit()
        db.refresh(obj)
        return obj

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
