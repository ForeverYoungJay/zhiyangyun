import uuid
from datetime import date

from sqlalchemy import String, Date, ForeignKey, Integer, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class MiniappServiceRequest(Base, TenantBaseMixin):
    __tablename__ = "miniapp_service_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    request_type: Mapped[str] = mapped_column(String(30), nullable=False, default="repair")
    content: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")


class FamilyAccount(Base, TenantBaseMixin):
    __tablename__ = "family_accounts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    relation: Mapped[str] = mapped_column(String(20), nullable=False)


class FamilyVisit(Base, TenantBaseMixin):
    __tablename__ = "family_visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("family_accounts.id"), nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="booked")


class DashboardMetric(Base, TenantBaseMixin):
    __tablename__ = "dashboard_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    occupancy_rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    revenue: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    alerts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
