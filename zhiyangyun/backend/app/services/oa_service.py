from datetime import date, datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.models.oa import (
    ApprovalRequest,
    NotificationMessage,
    ShiftAssignment,
    ShiftTemplate,
    TrainingCourse,
    TrainingRecord,
)
from app.models.user import User
from app.schemas.oa import (
    ApprovalRequestCreate,
    NotificationMessageCreate,
    ShiftAssignmentCreate,
    ShiftAssignmentStatusUpdate,
    ShiftTemplateCreate,
    TrainingCourseCreate,
    TrainingRecordCreate,
)


class OAService:
    def _save(self, db: Session, obj):
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def _to_plain(self, obj):
        if obj is None:
            return {}
        mapper = inspect(obj).mapper
        return {attr.key: getattr(obj, attr.key) for attr in mapper.column_attrs}

    def _pager(self, rows: list, page: int, page_size: int):
        total = len(rows)
        start = (page - 1) * page_size
        return {
            "items": rows[start:start + page_size],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

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

    def list_shifts(self, db: Session, tenant_id: str, page: int = 1, page_size: int = 10, keyword: str = "", status: str = ""):
        stmt = select(ShiftTemplate).where(ShiftTemplate.tenant_id == tenant_id)
        if keyword:
            like_kw = f"%{keyword.strip()}%"
            stmt = stmt.where(
                or_(
                    ShiftTemplate.name.like(like_kw),
                    ShiftTemplate.start_time.like(like_kw),
                    ShiftTemplate.end_time.like(like_kw),
                )
            )
        if status:
            stmt = stmt.where(ShiftTemplate.status == status)
        rows = [self._to_plain(x) for x in db.scalars(stmt.order_by(ShiftTemplate.id.desc())).all()]
        return self._pager(rows, page, page_size)

    def create_shift(self, db: Session, tenant_id: str, payload: ShiftTemplateCreate):
        if self._time_to_minute(payload.start_time) >= self._time_to_minute(payload.end_time):
            raise ValueError("班次开始时间必须早于结束时间")

        duplicate = db.scalar(
            select(ShiftTemplate).where(
                ShiftTemplate.tenant_id == tenant_id,
                ShiftTemplate.name == payload.name,
                ShiftTemplate.start_time == payload.start_time,
                ShiftTemplate.end_time == payload.end_time,
            )
        )
        if duplicate:
            raise ValueError("已存在同名同时间班次模板")

        return self._save(db, ShiftTemplate(tenant_id=tenant_id, **payload.model_dump()))

    def list_assignments(
        self,
        db: Session,
        tenant_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: str = "",
        status: str = "",
        shift_id: str = "",
        user_id: str = "",
        duty_date: str = "",
        start_date: str = "",
        end_date: str = "",
    ):
        stmt = (
            select(
                ShiftAssignment,
                ShiftTemplate.name.label("shift_name"),
                ShiftTemplate.start_time.label("shift_start_time"),
                ShiftTemplate.end_time.label("shift_end_time"),
                User.real_name.label("user_name"),
                User.username.label("username"),
            )
            .join(ShiftTemplate, ShiftTemplate.id == ShiftAssignment.shift_id)
            .join(User, User.id == ShiftAssignment.user_id)
            .where(
                ShiftAssignment.tenant_id == tenant_id,
                ShiftTemplate.tenant_id == tenant_id,
                User.tenant_id == tenant_id,
            )
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
            stmt = stmt.where(ShiftAssignment.duty_date == date.fromisoformat(duty_date))
        if start_date:
            stmt = stmt.where(ShiftAssignment.duty_date >= date.fromisoformat(start_date))
        if end_date:
            stmt = stmt.where(ShiftAssignment.duty_date <= date.fromisoformat(end_date))

        rows = db.execute(stmt.order_by(ShiftAssignment.duty_date.desc(), ShiftAssignment.id.desc())).all()
        payload = [
            {
                **self._to_plain(item),
                "shift_name": shift_name,
                "shift_start_time": shift_start_time,
                "shift_end_time": shift_end_time,
                "user_name": user_name,
                "display_name": user_name or username,
                "username": username,
            }
            for item, shift_name, shift_start_time, shift_end_time, user_name, username in rows
        ]
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
            .where(
                ShiftAssignment.tenant_id == tenant_id,
                ShiftAssignment.user_id == payload.user_id,
                ShiftAssignment.duty_date == payload.duty_date,
                ShiftAssignment.status.in_(["draft", "published", "executed", "assigned"]),
            )
        ).all()
        for existing, existing_shift in existing_rows:
            if self._overlap(shift.start_time, shift.end_time, existing_shift.start_time, existing_shift.end_time):
                raise ValueError(f"排班冲突：已存在班次 {existing_shift.name}({existing_shift.start_time}-{existing_shift.end_time})")

        obj = ShiftAssignment(tenant_id=tenant_id, **payload.model_dump())
        saved = self._save(db, obj)
        return {
            **self._to_plain(saved),
            "shift_name": shift.name,
            "shift_start_time": shift.start_time,
            "shift_end_time": shift.end_time,
            "user_name": user.real_name,
            "display_name": user.real_name or user.username,
            "username": user.username,
        }

    def update_assignment_status(self, db: Session, tenant_id: str, assignment_id: str, payload: ShiftAssignmentStatusUpdate, operator_id: str):
        obj = db.scalar(select(ShiftAssignment).where(ShiftAssignment.tenant_id == tenant_id, ShiftAssignment.id == assignment_id))
        if not obj:
            raise ValueError("排班记录不存在")

        action_map = {
            "publish": "published",
            "execute": "executed",
            "mark_exception": "exception",
            "reopen": "draft",
        }
        next_status = action_map.get(payload.action)
        if not next_status:
            raise ValueError("不支持的动作")

        allowed = {
            "draft": ["publish", "mark_exception"],
            "assigned": ["publish", "mark_exception"],
            "published": ["execute", "mark_exception", "reopen"],
            "executed": ["reopen"],
            "exception": ["reopen", "publish"],
        }
        if payload.action not in allowed.get(obj.status, []):
            raise ValueError(f"状态流转非法: {obj.status} -> {payload.action}")

        obj.status = next_status
        db.commit()
        db.refresh(obj)

        if payload.action == "publish":
            existed = db.scalar(
                select(ApprovalRequest).where(
                    ApprovalRequest.tenant_id == tenant_id,
                    ApprovalRequest.module == "oa1_shift",
                    ApprovalRequest.biz_id == obj.id,
                    ApprovalRequest.status == "pending",
                )
            )
            if not existed:
                db.add(
                    ApprovalRequest(
                        tenant_id=tenant_id,
                        module="oa1_shift",
                        biz_id=obj.id,
                        applicant_id=operator_id,
                        approver_id=None,
                        status="pending",
                        note=payload.note or f"排班发布审批：{obj.id}",
                    )
                )
                db.commit()
        return self._to_plain(obj)

    def list_approvals(self, db: Session, tenant_id: str):
        rows = db.execute(
            select(ApprovalRequest, User.real_name.label("applicant_name"), User.username.label("applicant_username"))
            .join(User, and_(User.id == ApprovalRequest.applicant_id, User.tenant_id == tenant_id))
            .where(ApprovalRequest.tenant_id == tenant_id)
            .order_by(ApprovalRequest.id.desc())
        ).all()
        return [
            {
                **self._to_plain(item),
                "applicant_name": applicant_name,
                "applicant_display_name": applicant_name or applicant_username,
            }
            for item, applicant_name, applicant_username in rows
        ]

    def create_approval(self, db: Session, tenant_id: str, payload: ApprovalRequestCreate):
        return self._save(db, ApprovalRequest(tenant_id=tenant_id, **payload.model_dump()))

    def list_notifications(self, db: Session, tenant_id: str):
        return db.scalars(select(NotificationMessage).where(NotificationMessage.tenant_id == tenant_id)).all()

    def create_notification(self, db: Session, tenant_id: str, payload: NotificationMessageCreate):
        return self._save(db, NotificationMessage(tenant_id=tenant_id, **payload.model_dump()))

    def list_courses(self, db: Session, tenant_id: str):
        return db.scalars(select(TrainingCourse).where(TrainingCourse.tenant_id == tenant_id)).all()

    def create_course(self, db: Session, tenant_id: str, payload: TrainingCourseCreate):
        return self._save(db, TrainingCourse(tenant_id=tenant_id, **payload.model_dump()))

    def list_records(self, db: Session, tenant_id: str):
        return db.scalars(select(TrainingRecord).where(TrainingRecord.tenant_id == tenant_id)).all()

    def create_record(self, db: Session, tenant_id: str, payload: TrainingRecordCreate):
        return self._save(db, TrainingRecord(tenant_id=tenant_id, **payload.model_dump()))
