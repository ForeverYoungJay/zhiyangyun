from datetime import date, datetime

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, aliased

from app.models.oa import (
    ApprovalActionLog,
    ApprovalRequest,
    NotificationMessage,
    ShiftAssignment,
    ShiftTemplate,
    TrainingCourse,
    TrainingRecord,
)
from app.models.user import User
from app.schemas.oa import (
    ApprovalActionPayload,
    ApprovalRequestCreate,
    NotificationActionPayload,
    NotificationMessageCreate,
    ShiftAssignmentCreate,
    ShiftAssignmentStatusUpdate,
    ShiftTemplateCreate,
    TrainingCourseCreate,
    TrainingRecordActionPayload,
    TrainingRecordCreate,
)


class OAService:
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
        return {"items": rows[start:start + page_size], "total": total, "page": page, "page_size": page_size}

    def _time_to_minute(self, value: str) -> int:
        try:
            hour, minute = value.split(":")
            return int(hour) * 60 + int(minute)
        except Exception:
            raise ValueError("时间格式错误，应为 HH:MM")

    def _overlap(self, start_a: str, end_a: str, start_b: str, end_b: str) -> bool:
        a1 = self._time_to_minute(start_a)
        a2 = self._time_to_minute(end_a)
        b1 = self._time_to_minute(start_b)
        b2 = self._time_to_minute(end_b)
        return max(a1, b1) < min(a2, b2)

    def suggest_users(self, db: Session, tenant_id: str, keyword: str = "", limit: int = 20):
        stmt = select(User).where(User.tenant_id == tenant_id, User.is_active == True)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(User.real_name.like(like_kw), User.username.like(like_kw)))
        users = db.scalars(stmt.order_by(User.real_name.asc()).limit(max(1, min(limit, 100)))).all()
        return [{"id": u.id, "real_name": u.real_name, "username": u.username, "display_name": u.real_name or u.username} for u in users]

    def list_shifts(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = ""):
        stmt = select(ShiftTemplate).where(ShiftTemplate.tenant_id == tenant_id)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ShiftTemplate.name.like(like_kw), ShiftTemplate.start_time.like(like_kw), ShiftTemplate.end_time.like(like_kw)))
        if status:
            stmt = stmt.where(ShiftTemplate.status == status)
        rows = [self._to_plain(x) for x in db.scalars(stmt.order_by(ShiftTemplate.id.desc())).all()]
        return self._pager(rows, page, page_size)

    def create_shift(self, db: Session, tenant_id: str, payload: ShiftTemplateCreate):
        if self._time_to_minute(payload.start_time) >= self._time_to_minute(payload.end_time):
            raise ValueError("班次开始时间必须早于结束时间")
        duplicate = db.scalar(select(ShiftTemplate).where(ShiftTemplate.tenant_id == tenant_id, ShiftTemplate.name == payload.name, ShiftTemplate.start_time == payload.start_time, ShiftTemplate.end_time == payload.end_time))
        if duplicate:
            raise ValueError("已存在同名同时间班次模板")
        return self._save(db, ShiftTemplate(tenant_id=tenant_id, **payload.model_dump()))

    def list_assignments(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", shift_id: str = "", user_id: str = "", duty_date: str = "", start_date: str = "", end_date: str = ""):
        stmt = (
            select(ShiftAssignment, ShiftTemplate.name.label("shift_name"), ShiftTemplate.start_time.label("shift_start_time"), ShiftTemplate.end_time.label("shift_end_time"), User.real_name.label("user_name"), User.username.label("username"))
            .join(ShiftTemplate, ShiftTemplate.id == ShiftAssignment.shift_id)
            .join(User, User.id == ShiftAssignment.user_id)
            .where(ShiftAssignment.tenant_id == tenant_id, ShiftTemplate.tenant_id == tenant_id, User.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ShiftTemplate.name.like(like_kw), User.real_name.like(like_kw), User.username.like(like_kw)))
        if status:
            stmt = stmt.where(ShiftAssignment.status == status)
        if shift_id:
            stmt = stmt.where(ShiftAssignment.shift_id == shift_id)
        if user_id:
            stmt = stmt.where(ShiftAssignment.user_id == user_id)
        if duty_date:
            stmt = stmt.where(ShiftAssignment.duty_date == duty_date)
        if start_date:
            stmt = stmt.where(ShiftAssignment.duty_date >= start_date)
        if end_date:
            stmt = stmt.where(ShiftAssignment.duty_date <= end_date)
        rows = db.execute(stmt.order_by(ShiftAssignment.duty_date.desc(), ShiftAssignment.id.desc())).all()
        payload = [{**self._to_plain(item), "shift_name": shift_name, "shift_start_time": shift_start_time, "shift_end_time": shift_end_time, "user_name": user_name, "display_name": user_name or username, "username": username} for item, shift_name, shift_start_time, shift_end_time, user_name, username in rows]
        return self._pager(payload, page, page_size)

    def create_assignment(self, db: Session, tenant_id: str, payload: ShiftAssignmentCreate):
        if payload.duty_date < date.today():
            raise ValueError("不能创建过去日期的排班")
        shift = db.scalar(select(ShiftTemplate).where(ShiftTemplate.tenant_id == tenant_id, ShiftTemplate.id == payload.shift_id))
        if not shift:
            raise ValueError("班次模板不存在")
        user = db.scalar(select(User).where(User.tenant_id == tenant_id, User.id == payload.user_id))
        if not user:
            raise ValueError("排班人员不存在")
        existing_rows = db.execute(
            select(ShiftAssignment, ShiftTemplate)
            .join(ShiftTemplate, ShiftTemplate.id == ShiftAssignment.shift_id)
            .where(ShiftAssignment.tenant_id == tenant_id, ShiftAssignment.user_id == payload.user_id, ShiftAssignment.duty_date == payload.duty_date, ShiftAssignment.status.in_(["draft", "published", "executed", "assigned"]))
        ).all()
        for _, existing_shift in existing_rows:
            if self._overlap(shift.start_time, shift.end_time, existing_shift.start_time, existing_shift.end_time):
                raise ValueError(f"排班冲突：已存在班次 {existing_shift.name}({existing_shift.start_time}-{existing_shift.end_time})")
        saved = self._save(db, ShiftAssignment(tenant_id=tenant_id, **payload.model_dump()))
        return {**self._to_plain(saved), "shift_name": shift.name, "shift_start_time": shift.start_time, "shift_end_time": shift.end_time, "user_name": user.real_name, "display_name": user.real_name or user.username, "username": user.username}

    def update_assignment_status(self, db: Session, tenant_id: str, assignment_id: str, payload: ShiftAssignmentStatusUpdate, operator_id: str):
        obj = db.scalar(select(ShiftAssignment).where(ShiftAssignment.tenant_id == tenant_id, ShiftAssignment.id == assignment_id))
        if not obj:
            raise ValueError("排班记录不存在")
        action_map = {"publish": "published", "execute": "executed", "mark_exception": "exception", "reopen": "draft"}
        next_status = action_map.get(payload.action)
        if not next_status:
            raise ValueError("不支持的动作")
        allowed = {"draft": ["publish", "mark_exception"], "assigned": ["publish", "mark_exception"], "published": ["execute", "mark_exception", "reopen"], "executed": ["reopen"], "exception": ["reopen", "publish"]}
        if payload.action not in allowed.get(obj.status, []):
            raise ValueError(f"状态流转非法: {obj.status} -> {payload.action}")
        obj.status = next_status
        db.commit()
        db.refresh(obj)
        if payload.action == "publish":
            existed = db.scalar(select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.module == "oa1_shift", ApprovalRequest.biz_id == obj.id, ApprovalRequest.status == "pending"))
            if not existed:
                db.add(ApprovalRequest(tenant_id=tenant_id, module="oa1_shift", biz_id=obj.id, applicant_id=operator_id, approver_id=None, status="pending", note=payload.note or f"排班发布审批：{obj.id}"))
                db.commit()
        return self._to_plain(obj)

    def list_approvals(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", module: str = ""):
        applicant = aliased(User)
        approver = aliased(User)
        stmt = (
            select(ApprovalRequest, applicant.real_name.label("applicant_name"), applicant.username.label("applicant_username"), approver.real_name.label("approver_name"), approver.username.label("approver_username"))
            .join(applicant, and_(applicant.id == ApprovalRequest.applicant_id, applicant.tenant_id == tenant_id))
            .outerjoin(approver, and_(approver.id == ApprovalRequest.approver_id, approver.tenant_id == tenant_id))
            .where(ApprovalRequest.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ApprovalRequest.biz_id.like(like_kw), ApprovalRequest.note.like(like_kw), applicant.real_name.like(like_kw), approver.real_name.like(like_kw)))
        if status:
            stmt = stmt.where(ApprovalRequest.status == status)
        if module:
            stmt = stmt.where(ApprovalRequest.module == module)
        rows = db.execute(stmt.order_by(ApprovalRequest.id.desc())).all()
        payload = []
        for item, applicant_name, applicant_username, approver_name, approver_username in rows:
            cc_names = []
            for uid in [x for x in (item.cc_user_ids or "").split(",") if x]:
                u = db.scalar(select(User).where(User.tenant_id == tenant_id, User.id == uid))
                if u:
                    cc_names.append(u.real_name or u.username)
            payload.append({**self._to_plain(item), "applicant_name": applicant_name, "applicant_display_name": applicant_name or applicant_username, "approver_name": approver_name, "approver_display_name": approver_name or approver_username, "cc_names": cc_names})
        return self._pager(payload, page, page_size)

    def create_approval(self, db: Session, tenant_id: str, payload: ApprovalRequestCreate, operator_id: str):
        request = ApprovalRequest(
            tenant_id=tenant_id,
            module=payload.module,
            biz_id=payload.biz_id,
            applicant_id=operator_id,
            approver_id=payload.approver_id,
            cc_user_ids=",".join(payload.cc_user_ids or []),
            total_steps=max(1, payload.total_steps),
            current_step=1,
            status="pending",
            note=payload.note,
        )
        saved = self._save(db, request)
        db.add(ApprovalActionLog(tenant_id=tenant_id, request_id=saved.id, action="submit", operator_id=operator_id, note=payload.note or "提交审批"))
        db.commit()
        return self._to_plain(saved)

    def action_approval(self, db: Session, tenant_id: str, request_id: str, payload: ApprovalActionPayload, operator_id: str):
        item = db.scalar(select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.id == request_id))
        if not item:
            raise ValueError("审批单不存在")
        if payload.action == "approve":
            if item.status not in ["pending", "in_review"]:
                raise ValueError("当前状态不可审批通过")
            if item.current_step >= item.total_steps:
                item.status = "approved"
                item.approved_at = datetime.utcnow()
                item.closed_at = datetime.utcnow()
            else:
                item.current_step += 1
                item.status = "in_review"
        elif payload.action == "reject":
            if item.status in ["approved", "rejected", "cancelled"]:
                raise ValueError("当前状态不可驳回")
            item.status = "rejected"
            item.rejected_at = datetime.utcnow()
            item.closed_at = datetime.utcnow()
        elif payload.action == "cancel":
            if item.status in ["approved", "cancelled"]:
                raise ValueError("当前状态不可撤销")
            item.status = "cancelled"
            item.closed_at = datetime.utcnow()
        else:
            raise ValueError("不支持的动作")
        db.add(ApprovalActionLog(tenant_id=tenant_id, request_id=item.id, action=payload.action, operator_id=operator_id, note=payload.note))
        db.commit()
        db.refresh(item)
        return self._to_plain(item)

    def list_approval_logs(self, db: Session, tenant_id: str, request_id: str):
        actor = aliased(User)
        rows = db.execute(
            select(ApprovalActionLog, actor.real_name, actor.username)
            .join(actor, and_(actor.id == ApprovalActionLog.operator_id, actor.tenant_id == tenant_id))
            .where(ApprovalActionLog.tenant_id == tenant_id, ApprovalActionLog.request_id == request_id)
            .order_by(ApprovalActionLog.acted_at.asc())
        ).all()
        return [{**self._to_plain(log), "operator_name": real_name or username} for log, real_name, username in rows]

    def list_notifications(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", channel: str = ""):
        target = aliased(User)
        stmt = (
            select(NotificationMessage, target.real_name, target.username)
            .outerjoin(target, and_(target.id == NotificationMessage.target_user_id, target.tenant_id == tenant_id))
            .where(NotificationMessage.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(NotificationMessage.title.like(like_kw), NotificationMessage.content.like(like_kw), target.real_name.like(like_kw)))
        if status:
            stmt = stmt.where(NotificationMessage.status == status)
        if channel:
            stmt = stmt.where(NotificationMessage.channel == channel)
        rows = db.execute(stmt.order_by(NotificationMessage.sent_at.desc(), NotificationMessage.id.desc())).all()
        payload = [{**self._to_plain(item), "target_name": real_name or username or "全员"} for item, real_name, username in rows]
        return self._pager(payload, page, page_size)

    def create_notification(self, db: Session, tenant_id: str, payload: NotificationMessageCreate):
        status = "sent" if payload.strategy == "immediate" else "pending"
        delivered_at = datetime.utcnow() if status == "sent" else None
        return self._save(db, NotificationMessage(tenant_id=tenant_id, status=status, delivered_at=delivered_at, **payload.model_dump()))

    def action_notification(self, db: Session, tenant_id: str, message_id: str, payload: NotificationActionPayload):
        item = db.scalar(select(NotificationMessage).where(NotificationMessage.tenant_id == tenant_id, NotificationMessage.id == message_id))
        if not item:
            raise ValueError("通知不存在")
        if payload.action == "deliver":
            item.status = "sent"
            item.delivered_at = datetime.utcnow()
        elif payload.action == "retry":
            item.retry_count += 1
            item.status = "retrying"
        elif payload.action == "fail":
            item.status = "failed"
        else:
            raise ValueError("不支持的动作")
        db.commit()
        db.refresh(item)
        return self._to_plain(item)

    def list_courses(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = ""):
        trainer = aliased(User)
        stmt = (
            select(TrainingCourse, trainer.real_name, trainer.username)
            .outerjoin(trainer, and_(trainer.id == TrainingCourse.trainer_id, trainer.tenant_id == tenant_id))
            .where(TrainingCourse.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(TrainingCourse.title.like(like_kw), TrainingCourse.category.like(like_kw), trainer.real_name.like(like_kw)))
        if status:
            stmt = stmt.where(TrainingCourse.status == status)
        rows = db.execute(stmt.order_by(TrainingCourse.id.desc())).all()
        payload = [{**self._to_plain(course), "trainer_name": real_name or username or "待定"} for course, real_name, username in rows]
        return self._pager(payload, page, page_size)

    def create_course(self, db: Session, tenant_id: str, payload: TrainingCourseCreate):
        if payload.start_date and payload.end_date and payload.start_date > payload.end_date:
            raise ValueError("培训开始日期不能晚于结束日期")
        return self._save(db, TrainingCourse(tenant_id=tenant_id, status="planned", **payload.model_dump()))

    def list_records(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = "", course_id: str = ""):
        trainee = aliased(User)
        evaluator = aliased(User)
        stmt = (
            select(TrainingRecord, TrainingCourse.title.label("course_title"), trainee.real_name.label("trainee_name"), trainee.username.label("trainee_username"), evaluator.real_name.label("evaluator_name"), evaluator.username.label("evaluator_username"))
            .join(TrainingCourse, and_(TrainingCourse.id == TrainingRecord.course_id, TrainingCourse.tenant_id == tenant_id))
            .join(trainee, and_(trainee.id == TrainingRecord.user_id, trainee.tenant_id == tenant_id))
            .outerjoin(evaluator, and_(evaluator.id == TrainingRecord.evaluator_id, evaluator.tenant_id == tenant_id))
            .where(TrainingRecord.tenant_id == tenant_id)
        )
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(TrainingCourse.title.like(like_kw), trainee.real_name.like(like_kw), trainee.username.like(like_kw)))
        if status:
            stmt = stmt.where(TrainingRecord.status == status)
        if course_id:
            stmt = stmt.where(TrainingRecord.course_id == course_id)
        rows = db.execute(stmt.order_by(TrainingRecord.id.desc())).all()
        payload = [{**self._to_plain(record), "course_title": course_title, "user_name": trainee_name or trainee_username, "evaluator_name": evaluator_name or evaluator_username or "-"} for record, course_title, trainee_name, trainee_username, evaluator_name, evaluator_username in rows]
        return self._pager(payload, page, page_size)

    def create_record(self, db: Session, tenant_id: str, payload: TrainingRecordCreate):
        existed = db.scalar(select(TrainingRecord).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.course_id == payload.course_id, TrainingRecord.user_id == payload.user_id))
        if existed:
            raise ValueError("该学员已加入本课程")
        return self._save(db, TrainingRecord(tenant_id=tenant_id, **payload.model_dump()))

    def action_record(self, db: Session, tenant_id: str, record_id: str, payload: TrainingRecordActionPayload, operator_id: str):
        item = db.scalar(select(TrainingRecord).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.id == record_id))
        if not item:
            raise ValueError("培训记录不存在")
        if payload.action == "sign_in":
            item.attendance_status = "present"
            item.attended_at = datetime.utcnow()
            item.status = "learning"
        elif payload.action == "absent":
            item.attendance_status = "absent"
            item.status = "failed"
        elif payload.action == "assess":
            if payload.score is None:
                raise ValueError("考核动作必须传 score")
            item.score = payload.score
            item.exam_status = "passed" if payload.score >= 60 else "failed"
            item.status = "completed" if payload.score >= 60 and item.attendance_status == "present" else "failed"
            item.evaluator_id = operator_id
            item.assessed_at = datetime.utcnow()
            item.completed_on = date.today()
        else:
            raise ValueError("不支持的动作")
        item.remark = payload.remark or item.remark
        db.commit()
        db.refresh(item)
        return self._to_plain(item)

    def course_closure_stats(self, db: Session, tenant_id: str, course_id: str):
        total = db.scalar(select(func.count(TrainingRecord.id)).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.course_id == course_id)) or 0
        signed = db.scalar(select(func.count(TrainingRecord.id)).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.course_id == course_id, TrainingRecord.attendance_status == "present")) or 0
        passed = db.scalar(select(func.count(TrainingRecord.id)).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.course_id == course_id, TrainingRecord.exam_status == "passed")) or 0
        closed = db.scalar(select(func.count(TrainingRecord.id)).where(TrainingRecord.tenant_id == tenant_id, TrainingRecord.course_id == course_id, TrainingRecord.status == "completed")) or 0
        return {"course_id": course_id, "total": total, "signed_in": signed, "passed": passed, "closed_loop": closed, "closure_rate": round((closed / total) * 100, 2) if total else 0}
