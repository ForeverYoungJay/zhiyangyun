from datetime import date
from pydantic import BaseModel, Field


class FamilyServiceOrderCreate(BaseModel):
    elder_id: str
    package_id: str
    start_date: date | None = None


class MiniappServiceRequestCreate(BaseModel):
    elder_id: str
    request_type: str = "repair"
    content: str


class FamilyAccountCreate(BaseModel):
    elder_id: str
    name: str
    phone: str
    relation: str


class FamilyVisitCreate(BaseModel):
    family_id: str
    visit_date: date


class DashboardMetricCreate(BaseModel):
    metric_date: date
    occupancy_rate: float = 0
    revenue: float = 0
    alerts: int = 0


class FamilySurveyCreate(BaseModel):
    elder_id: str
    family_id: str | None = None
    score: int = Field(default=5, ge=1, le=5)
    comment: str = ""
