import uuid
from datetime import datetime, date

from sqlalchemy import String, Date, DateTime, ForeignKey, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class ServiceItem(Base, TenantBaseMixin):
    __tablename__ = "service_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="care")
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class CarePackage(Base, TenantBaseMixin):
    __tablename__ = "care_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    period: Mapped[str] = mapped_column(String(20), nullable=False, default="daily")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class CarePackageItem(Base, TenantBaseMixin):
    __tablename__ = "care_package_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("care_packages.id"), nullable=False)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("service_items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ElderPackage(Base, TenantBaseMixin):
    __tablename__ = "elder_packages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    package_id: Mapped[str] = mapped_column(String(36), ForeignKey("care_packages.id"), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")


class CareTask(Base, TenantBaseMixin):
    __tablename__ = "care_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("service_items.id"), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    qr_scan_in: Mapped[str] = mapped_column(Text, nullable=False, default="")
    qr_scan_out: Mapped[str] = mapped_column(Text, nullable=False, default="")
    supervise_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
