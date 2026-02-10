"""init m1 assets

Revision ID: 2026021101
Revises:
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021101"
down_revision = None
branch_labels = None
depends_on = None


def create_tenant_cols(table):
    table.append_column(sa.Column("tenant_id", sa.String(length=36), nullable=False))


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("real_name", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])

    op.create_table(
        "roles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_index("ix_roles_tenant_id", "roles", ["tenant_id"])

    op.create_table(
        "permissions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_index("ix_permissions_tenant_id", "permissions", ["tenant_id"])

    op.create_table(
        "user_roles",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role_id", sa.String(length=36), sa.ForeignKey("roles.id"), nullable=False),
    )
    op.create_index("ix_user_roles_tenant_id", "user_roles", ["tenant_id"])

    op.create_table(
        "role_permissions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("role_id", sa.String(length=36), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("permission_id", sa.String(length=36), sa.ForeignKey("permissions.id"), nullable=False),
    )
    op.create_index("ix_role_permissions_tenant_id", "role_permissions", ["tenant_id"])

    op.create_table(
        "buildings",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False, unique=True),
    )
    op.create_index("ix_buildings_tenant_id", "buildings", ["tenant_id"])

    op.create_table(
        "floors",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("building_id", sa.String(length=36), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("floor_no", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
    )
    op.create_index("ix_floors_tenant_id", "floors", ["tenant_id"])

    op.create_table(
        "rooms",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("building_id", sa.String(length=36), sa.ForeignKey("buildings.id"), nullable=False),
        sa.Column("floor_id", sa.String(length=36), sa.ForeignKey("floors.id"), nullable=False),
        sa.Column("room_no", sa.String(length=30), nullable=False),
        sa.Column("room_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_rooms_tenant_id", "rooms", ["tenant_id"])

    op.create_table(
        "beds",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("room_id", sa.String(length=36), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("bed_no", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("qr_code", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_beds_tenant_id", "beds", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("beds")
    op.drop_table("rooms")
    op.drop_table("floors")
    op.drop_table("buildings")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("users")
