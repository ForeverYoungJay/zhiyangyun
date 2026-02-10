from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from app.models.mixins import UUIDPKMixin, TenantMixin, TimestampMixin


class User(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Role(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_roles_tenant_code"),)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Permission(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "permissions"
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class UserRole(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("tenant_id", "user_id", "role_id", name="uq_user_roles_tenant_user_role"),)
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)


class RolePermission(Base, UUIDPKMixin, TenantMixin, TimestampMixin):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("tenant_id", "role_id", "permission_id", name="uq_role_permissions_tenant_role_perm"),)
    role_id = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
