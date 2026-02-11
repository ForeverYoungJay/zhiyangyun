from datetime import datetime, date
from pydantic import BaseModel, Field


class ServiceItemCreate(BaseModel):
    name: str
    category: str = "care"
    unit_price: float = 0
    duration_min: int = 30


class CarePackageCreate(BaseModel):
    name: str
    period: str = "daily"


class CarePackageItemCreate(BaseModel):
    package_id: str
    item_id: str
    quantity: int = 1


class ElderPackageCreate(BaseModel):
    elder_id: str
    package_id: str
    start_date: date


class TaskGenerateRequest(BaseModel):
    elder_package_id: str
    scheduled_at: datetime


class TaskScanRequest(BaseModel):
    qr_value: str = Field(min_length=3)


class TaskSuperviseRequest(BaseModel):
    score: int = Field(ge=0, le=100)
