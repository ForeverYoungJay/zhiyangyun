import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, ForeignKey, Numeric, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class MedicationOrder(Base, TenantBaseMixin):
    __tablename__ = "medication_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    drug_name: Mapped[str] = mapped_column(String(100), nullable=False)
    dosage: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    frequency: Mapped[str] = mapped_column(String(50), nullable=False, default="qd")
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class MedicationExecution(Base, TenantBaseMixin):
    __tablename__ = "medication_executions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("medication_orders.id"), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    executor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    result: Mapped[str] = mapped_column(String(20), nullable=False, default="done")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")


class MealPlan(Base, TenantBaseMixin):
    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False, default="lunch")
    nutrition_tag: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")


class MealOrder(Base, TenantBaseMixin):
    __tablename__ = "meal_orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    plan_id: Mapped[str] = mapped_column(String(36), ForeignKey("meal_plans.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ordered")


class VitalSignRecord(Base, TenantBaseMixin):
    __tablename__ = "vital_sign_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    temperature: Mapped[float] = mapped_column(Numeric(4, 1), nullable=False, default=36.5)
    systolic: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    diastolic: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    pulse: Mapped[int] = mapped_column(Integer, nullable=False, default=75)


class HealthAssessment(Base, TenantBaseMixin):
    __tablename__ = "health_assessments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    assessed_on: Mapped[date] = mapped_column(Date, nullable=False)
    adl_score: Mapped[int] = mapped_column(Integer, nullable=False, default=60)
    mmse_score: Mapped[int] = mapped_column(Integer, nullable=False, default=24)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")


class BillingItem(Base, TenantBaseMixin):
    __tablename__ = "billing_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    charged_on: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="unpaid")


class BillingInvoice(Base, TenantBaseMixin):
    __tablename__ = "billing_invoices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    period_month: Mapped[str] = mapped_column(String(7), nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    paid_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
