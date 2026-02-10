from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, TimestampMixin


class Building(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "buildings"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_buildings_tenant_code"),)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)


class Floor(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "floors"
    __table_args__ = (UniqueConstraint("tenant_id", "building_id", "floor_no", name="uq_floors_tenant_building_floor"),)
    building_id = mapped_column(ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    floor_no: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str | None] = mapped_column(String(50), nullable=True)


class Room(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "rooms"
    __table_args__ = (UniqueConstraint("tenant_id", "building_id", "room_no", name="uq_rooms_tenant_building_room"),)
    building_id = mapped_column(ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False, index=True)
    floor_id = mapped_column(ForeignKey("floors.id", ondelete="RESTRICT"), nullable=False, index=True)
    room_no: Mapped[str] = mapped_column(String(20), nullable=False)
    room_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    qr_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class Bed(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "beds"
    __table_args__ = (UniqueConstraint("tenant_id", "room_id", "bed_no", name="uq_beds_tenant_room_bed"),)
    room_id = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"), nullable=False, index=True)
    bed_no: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="vacant", nullable=False)
    qr_code: Mapped[str | None] = mapped_column(String(255), nullable=True)
