from datetime import date
from pydantic import BaseModel


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
