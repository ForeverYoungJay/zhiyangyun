from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String


class Base(DeclarativeBase):
    pass


class TenantBaseMixin:
    tenant_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
