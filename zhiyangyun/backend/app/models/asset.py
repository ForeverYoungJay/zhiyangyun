import uuid
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TenantBaseMixin


class Building(Base, TenantBaseMixin):
    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)


class Floor(Base, TenantBaseMixin):
    __tablename__ = "floors"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False, index=True)
    floor_no: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Room(Base, TenantBaseMixin):
    __tablename__ = "rooms"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    building_id: Mapped[str] = mapped_column(String(36), ForeignKey("buildings.id"), nullable=False, index=True)
    floor_id: Mapped[str] = mapped_column(String(36), ForeignKey("floors.id"), nullable=False, index=True)
    room_no: Mapped[str] = mapped_column(String(30), nullable=False)
    room_type: Mapped[str] = mapped_column(String(30), nullable=False, default="double")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="available")


class Bed(Base, TenantBaseMixin):
    __tablename__ = "beds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id: Mapped[str] = mapped_column(String(36), ForeignKey("rooms.id"), nullable=False, index=True)
    bed_no: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="vacant")
    qr_code: Mapped[str] = mapped_column(String(255), nullable=False)
