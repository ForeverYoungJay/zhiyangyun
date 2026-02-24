import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class ShiftTemplate(Base, TenantBaseMixin):
    __tablename__ = "shift_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class ShiftAssignment(Base, TenantBaseMixin):
    __tablename__ = "shift_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    shift_id: Mapped[str] = mapped_column(String(36), ForeignKey("shift_templates.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    duty_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")


class ApprovalRequest(Base, TenantBaseMixin):
    __tablename__ = "approval_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    module: Mapped[str] = mapped_column(String(30), nullable=False)
    biz_id: Mapped[str] = mapped_column(String(36), nullable=False)
    applicant_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    approver_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    cc_user_ids: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    current_step: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    total_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")


class ApprovalActionLog(Base, TenantBaseMixin):
    __tablename__ = "approval_action_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), ForeignKey("approval_requests.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    operator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    acted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class NotificationMessage(Base, TenantBaseMixin):
    __tablename__ = "notification_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False, default="in_app")
    receiver_scope: Mapped[str] = mapped_column(String(20), nullable=False, default="all")
    target_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    strategy: Mapped[str] = mapped_column(String(30), nullable=False, default="immediate")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class TrainingCourse(Base, TenantBaseMixin):
    __tablename__ = "training_courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="service")
    trainer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    required_score: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")


class TrainingRecord(Base, TenantBaseMixin):
    __tablename__ = "training_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    course_id: Mapped[str] = mapped_column(String(36), ForeignKey("training_courses.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    attendance_status: Mapped[str] = mapped_column(String(20), nullable=False, default="unsigned")
    attended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exam_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    assessed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    evaluator_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    completed_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="learning")
    remark: Mapped[str] = mapped_column(Text, nullable=False, default="")
