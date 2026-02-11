from datetime import datetime, date
from pydantic import BaseModel, Field


class ServiceItemCreate(BaseModel):
    name: str
    category: str = "care"
    unit_price: float = 0
    duration_min: int = 30


class ServiceItemStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|disabled)$")


class CarePackageCreate(BaseModel):
    name: str
    period: str = "daily"
    default_months: int = 6


class CarePackageStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|disabled)$")


class CarePackageItemCreate(BaseModel):
    package_id: str
    item_id: str
    quantity: int = 1


class ElderPackageCreate(BaseModel):
    elder_id: str
    package_id: str
    start_date: date


class CarePackageAssignmentCreate(BaseModel):
    package_id: str
    caregiver_id: str
    start_date: date
    months: int = 6


class TaskGenerateRequest(BaseModel):
    elder_package_id: str
    scheduled_at: datetime


class DispatchTasksRequest(BaseModel):
    elder_package_id: str
    dispatch_type: str = Field(default="periodic", pattern="^(periodic|emergency)$")
    frequency: str = Field(default="day", pattern="^(day|month|quarter|year|custom)$")
    custom_times: int = 1
    start_at: datetime


class RoundTaskCreate(BaseModel):
    elder_id: str
    item_id: str
    round_type: str = Field(pattern="^(nursing_round|admin_round)$")
    scheduled_at: datetime
    assigned_to: str | None = None


class TaskScanRequest(BaseModel):
    qr_value: str = Field(min_length=3)


class TaskSuperviseRequest(BaseModel):
    score: int = Field(ge=0, le=100)


class TaskIssueReportRequest(BaseModel):
    photo_urls: list[str] = Field(default_factory=list)
    description: str = ""
    report_to_dean: bool = True


class DeanReviewRequest(BaseModel):
    approved: bool = True
    note: str = ""
    deduction_score: int = Field(default=0, ge=0, le=100)
