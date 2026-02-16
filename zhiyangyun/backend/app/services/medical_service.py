from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import select, func, or_, and_
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
    BillingEvent,
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
    BillingInvoiceGenerate,
    BillingInvoiceWriteoff,
    BillingInvoiceException,
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

    def list_billing_items(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
        elder_id: str = "",
        start_date: str = "",
        end_date: str = "",
    ):
        stmt = (
            select(BillingItem, Elder.name.label("elder_name"), Elder.elder_no.label("elder_no"))
            .join(Elder, Elder.id == BillingItem.elder_id)
            .where(BillingItem.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(BillingItem.item_name.like(like_kw), Elder.name.like(like_kw), Elder.elder_no.like(like_kw)))
        if status:
            stmt = stmt.where(BillingItem.status == status)
        if elder_id:
            stmt = stmt.where(BillingItem.elder_id == elder_id)
        if start_date:
            stmt = stmt.where(BillingItem.charged_on >= start_date)
        if end_date:
            stmt = stmt.where(BillingItem.charged_on <= end_date)

        rows = db.execute(stmt.order_by(BillingItem.charged_on.desc(), BillingItem.id.desc())).all()
        payload = [
            {**self._to_plain(item), "elder_name": elder_name, "elder_no": elder_no}
            for item, elder_name, elder_no in rows
        ]
        return self._pager(payload, page, page_size)

    def create_billing_item(self, db: Session, tenant_id: str, payload: BillingItemCreate):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        obj = BillingItem(tenant_id=tenant_id, status="unpaid", **payload.model_dump())
        saved = self._save(db, obj)
        return {**self._to_plain(saved), "elder_name": elder.name, "elder_no": elder.elder_no}

    def _invoice_status_from_amount(self, total_amount: Decimal, paid_amount: Decimal, current_status: str = "open"):
        if current_status in ["disputed", "waived"]:
            return current_status
        if paid_amount <= 0:
            return "open"
        if paid_amount < total_amount:
            return "partial"
        return "paid"

    def _save_event(self, db: Session, tenant_id: str, invoice_id: str, event_type: str, amount: Decimal = Decimal("0"), note: str = "", user_id: str | None = None):
        db.add(BillingEvent(
            tenant_id=tenant_id,
            invoice_id=invoice_id,
            event_type=event_type,
            amount=amount,
            note=note,
            created_by=user_id,
        ))

    def _month_range(self, period_month: str):
        month_start = datetime.strptime(f"{period_month}-01", "%Y-%m-%d").date()
        if month_start.month == 12:
            month_end = date(month_start.year + 1, 1, 1)
        else:
            month_end = date(month_start.year, month_start.month + 1, 1)
        return month_start, month_end

    def list_invoices(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
        elder_id: str = "",
        period_month: str = "",
    ):
        stmt = (
            select(BillingInvoice, Elder.name.label("elder_name"), Elder.elder_no.label("elder_no"))
            .join(Elder, Elder.id == BillingInvoice.elder_id)
            .where(BillingInvoice.tenant_id == tenant_id, Elder.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(Elder.name.like(like_kw), Elder.elder_no.like(like_kw), BillingInvoice.period_month.like(like_kw)))
        if status:
            stmt = stmt.where(BillingInvoice.status == status)
        if elder_id:
            stmt = stmt.where(BillingInvoice.elder_id == elder_id)
        if period_month:
            stmt = stmt.where(BillingInvoice.period_month == period_month)

        rows = db.execute(stmt.order_by(BillingInvoice.period_month.desc(), BillingInvoice.id.desc())).all()
        payload = [
            {
                **self._to_plain(invoice),
                "elder_name": elder_name,
                "elder_no": elder_no,
                "unpaid_amount": float(Decimal(str(invoice.total_amount)) - Decimal(str(invoice.paid_amount))),
            }
            for invoice, elder_name, elder_no in rows
        ]
        return self._pager(payload, page, page_size)

    def create_invoice(self, db: Session, tenant_id: str, payload: BillingInvoiceCreate):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        existed = db.scalar(select(BillingInvoice).where(
            BillingInvoice.tenant_id == tenant_id,
            BillingInvoice.elder_id == payload.elder_id,
            BillingInvoice.period_month == payload.period_month,
        ))
        if existed:
            raise ValueError("该长者账期发票已存在，请改用账单生成或核销流程")
        total_amount = Decimal(str(payload.total_amount))
        obj = BillingInvoice(
            tenant_id=tenant_id,
            elder_id=payload.elder_id,
            period_month=payload.period_month,
            total_amount=total_amount,
            paid_amount=Decimal("0"),
            status="open",
        )
        db.add(obj)
        db.flush()
        self._save_event(db, tenant_id, obj.id, "created", amount=total_amount, note="手工创建发票")
        db.commit()
        db.refresh(obj)
        return {**self._to_plain(obj), "elder_name": elder.name, "elder_no": elder.elder_no}

    def generate_invoice(self, db: Session, tenant_id: str, payload: BillingInvoiceGenerate, user_id: str):
        elder = self._resolve_elder(db, tenant_id, payload.elder_id)
        existed = db.scalar(select(BillingInvoice).where(
            BillingInvoice.tenant_id == tenant_id,
            BillingInvoice.elder_id == payload.elder_id,
            BillingInvoice.period_month == payload.period_month,
        ))
        if existed:
            raise ValueError("发票已存在，请直接核销或异常处理")
        month_start, month_end = self._month_range(payload.period_month)
        month_amount = db.scalar(select(func.coalesce(func.sum(BillingItem.amount), 0)).where(
            BillingItem.tenant_id == tenant_id,
            BillingItem.elder_id == payload.elder_id,
            BillingItem.charged_on >= month_start,
            BillingItem.charged_on < month_end,
            BillingItem.status != "waived",
        )) or 0
        total_amount = Decimal(str(month_amount))
        invoice = BillingInvoice(
            tenant_id=tenant_id,
            elder_id=payload.elder_id,
            period_month=payload.period_month,
            total_amount=total_amount,
            paid_amount=Decimal("0"),
            status="open",
        )
        db.add(invoice)
        db.flush()
        self._save_event(db, tenant_id, invoice.id, "generated", total_amount, "系统按账单生成", user_id)
        db.commit()
        db.refresh(invoice)
        return {**self._to_plain(invoice), "elder_name": elder.name, "elder_no": elder.elder_no}

    def writeoff_invoice(self, db: Session, tenant_id: str, invoice_id: str, payload: BillingInvoiceWriteoff, user_id: str):
        invoice = db.scalar(select(BillingInvoice).where(BillingInvoice.tenant_id == tenant_id, BillingInvoice.id == invoice_id))
        if not invoice:
            raise ValueError("发票不存在")
        if invoice.status in ["waived"]:
            raise ValueError("已豁免发票不可核销")
        amount = Decimal(str(payload.amount))
        if amount <= 0:
            raise ValueError("核销金额必须大于0")
        total_amount = Decimal(str(invoice.total_amount))
        paid_amount = Decimal(str(invoice.paid_amount)) + amount
        if paid_amount > total_amount:
            raise ValueError("核销金额超过应收总额")
        invoice.paid_amount = paid_amount
        invoice.status = self._invoice_status_from_amount(total_amount, paid_amount, invoice.status)

        month_start, month_end = self._month_range(invoice.period_month)
        if invoice.status == "paid":
            db.execute(
                BillingItem.__table__.update().where(
                    and_(
                        BillingItem.tenant_id == tenant_id,
                        BillingItem.elder_id == invoice.elder_id,
                        BillingItem.charged_on >= month_start,
                        BillingItem.charged_on < month_end,
                        BillingItem.status.in_(["unpaid", "partial", "overdue"]),
                    )
                ).values(status="paid")
            )
        elif invoice.status == "partial":
            db.execute(
                BillingItem.__table__.update().where(
                    and_(
                        BillingItem.tenant_id == tenant_id,
                        BillingItem.elder_id == invoice.elder_id,
                        BillingItem.charged_on >= month_start,
                        BillingItem.charged_on < month_end,
                        BillingItem.status == "unpaid",
                    )
                ).values(status="partial")
            )
        # partial 状态仅影响当月未付账单条目
        self._save_event(db, tenant_id, invoice.id, "writeoff", amount, payload.note, user_id)
        db.commit()
        db.refresh(invoice)
        return invoice

    def handle_invoice_exception(self, db: Session, tenant_id: str, invoice_id: str, payload: BillingInvoiceException, user_id: str):
        invoice = db.scalar(select(BillingInvoice).where(BillingInvoice.tenant_id == tenant_id, BillingInvoice.id == invoice_id))
        if not invoice:
            raise ValueError("发票不存在")
        mapping = {
            "mark_overdue": "overdue",
            "mark_disputed": "disputed",
            "waive": "waived",
            "reopen": "open",
        }
        if payload.action not in mapping:
            raise ValueError("不支持的异常动作")
        next_status = mapping[payload.action]
        if payload.action == "reopen" and invoice.status not in ["overdue", "disputed"]:
            raise ValueError("仅逾期/争议发票可重开")
        if payload.action == "waive" and Decimal(str(invoice.paid_amount)) > 0:
            raise ValueError("已有核销金额的发票不可直接豁免")

        invoice.status = next_status
        event_amount = Decimal("0")
        month_start, month_end = self._month_range(invoice.period_month)
        if next_status == "waived":
            event_amount = Decimal(str(invoice.total_amount))
            db.execute(
                BillingItem.__table__.update().where(
                    and_(
                        BillingItem.tenant_id == tenant_id,
                        BillingItem.elder_id == invoice.elder_id,
                        BillingItem.charged_on >= month_start,
                        BillingItem.charged_on < month_end,
                        BillingItem.status.in_(["unpaid", "partial", "overdue"]),
                    )
                ).values(status="waived")
            )
        elif next_status == "overdue":
            db.execute(
                BillingItem.__table__.update().where(
                    and_(
                        BillingItem.tenant_id == tenant_id,
                        BillingItem.elder_id == invoice.elder_id,
                        BillingItem.charged_on >= month_start,
                        BillingItem.charged_on < month_end,
                        BillingItem.status.in_(["unpaid", "partial"]),
                    )
                ).values(status="overdue")
            )
        elif next_status == "open":
            invoice.status = self._invoice_status_from_amount(Decimal(str(invoice.total_amount)), Decimal(str(invoice.paid_amount)), "open")
        self._save_event(db, tenant_id, invoice.id, payload.action, event_amount, payload.note, user_id)
        db.commit()
        db.refresh(invoice)
        return invoice

    def list_invoice_events(self, db: Session, tenant_id: str, invoice_id: str):
        rows = db.scalars(select(BillingEvent).where(BillingEvent.tenant_id == tenant_id, BillingEvent.invoice_id == invoice_id).order_by(BillingEvent.created_at.desc(), BillingEvent.id.desc())).all()
        return [self._to_plain(x) for x in rows]
