from datetime import date
from pydantic import BaseModel


class ShiftTemplateCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    status: str = "draft"


class ShiftAssignmentCreate(BaseModel):
    shift_id: str
    user_id: str
    duty_date: date
    status: str = "draft"


class ShiftAssignmentStatusUpdate(BaseModel):
    action: str
    note: str = ""


class ApprovalRequestCreate(BaseModel):
    module: str
    biz_id: str
    approver_id: str | None = None
    cc_user_ids: list[str] = []
    total_steps: int = 1
    note: str = ""


class ApprovalActionPayload(BaseModel):
    action: str
    note: str = ""


class NotificationMessageCreate(BaseModel):
    title: str
    content: str
    channel: str = "in_app"
    receiver_scope: str = "all"
    target_user_id: str | None = None
    strategy: str = "immediate"


class NotificationActionPayload(BaseModel):
    action: str
    note: str = ""


class TrainingCourseCreate(BaseModel):
    title: str
    category: str = "service"
    trainer_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    required_score: int = 60


class TrainingRecordCreate(BaseModel):
    course_id: str
    user_id: str


class TrainingRecordActionPayload(BaseModel):
    action: str
    score: int | None = None
    remark: str = ""
