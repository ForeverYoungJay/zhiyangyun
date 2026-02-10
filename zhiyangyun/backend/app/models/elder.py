import uuid
from datetime import date, datetime

from sqlalchemy import String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class CrmLead(Base, TenantBaseMixin):
    __tablename__ = "crm_leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    source_channel: Mapped[str] = mapped_column(String(30), nullable=False, default="unknown")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="new")
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")


class Elder(Base, TenantBaseMixin):
    __tablename__ = "elders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("crm_leads.id"), nullable=True)
    elder_no: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False, default="unknown")
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    id_card: Mapped[str] = mapped_column(String(30), nullable=False, default="")
    care_level: Mapped[str] = mapped_column(String(20), nullable=False, default="L1")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="prospect")
    admission_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    discharge_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    building_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=True)
    floor_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("floors.id"), nullable=True)
    room_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("rooms.id"), nullable=True)
    bed_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("beds.id"), nullable=True)


class ElderChangeLog(Base, TenantBaseMixin):
    __tablename__ = "elder_change_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    elder_id: Mapped[str] = mapped_column(String(36), ForeignKey("elders.id"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
