from datetime import date
from pydantic import BaseModel


class ShiftTemplateCreate(BaseModel):
    name: str
    start_time: str
    end_time: str


class ShiftAssignmentCreate(BaseModel):
    shift_id: str
    user_id: str
    duty_date: date


class ApprovalRequestCreate(BaseModel):
    module: str
    biz_id: str
    applicant_id: str
    approver_id: str | None = None
    note: str = ""


class NotificationMessageCreate(BaseModel):
    title: str
    content: str
    channel: str = "in_app"
    receiver_scope: str = "all"


class TrainingCourseCreate(BaseModel):
    title: str
    category: str = "service"
    required_score: int = 60


class TrainingRecordCreate(BaseModel):
    course_id: str
    user_id: str
    score: int = 0
