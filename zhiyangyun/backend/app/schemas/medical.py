from datetime import date, datetime
from pydantic import BaseModel


class MedicationOrderCreate(BaseModel):
    elder_id: str
    drug_name: str
    dosage: str = ""
    frequency: str = "qd"
    start_date: date


class MedicationExecutionCreate(BaseModel):
    order_id: str
    result: str = "done"
    note: str = ""


class MealPlanCreate(BaseModel):
    name: str
    plan_date: date
    meal_type: str = "lunch"
    nutrition_tag: str = "normal"
    note: str = ""


class MealOrderCreate(BaseModel):
    elder_id: str
    plan_id: str


class VitalSignCreate(BaseModel):
    elder_id: str
    temperature: float = 36.5
    systolic: int = 120
    diastolic: int = 80
    pulse: int = 75


class HealthAssessmentCreate(BaseModel):
    elder_id: str
    assessed_on: date
    adl_score: int = 60
    mmse_score: int = 24
    risk_level: str = "medium"


class AssessmentClosePayload(BaseModel):
    note: str = ""


class BillingItemCreate(BaseModel):
    elder_id: str
    item_name: str
    amount: float
    charged_on: date


class BillingInvoiceCreate(BaseModel):
    elder_id: str
    period_month: str
    total_amount: float


class MedicationOrderOut(MedicationOrderCreate):
    id: str
    status: str
    model_config = {"from_attributes": True}
