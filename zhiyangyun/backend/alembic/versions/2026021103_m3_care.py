"""m3 care standardization

Revision ID: 2026021103
Revises: 2026021102
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021103"
down_revision = "2026021102"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "service_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=30), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("duration_min", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_service_items_tenant_id", "service_items", ["tenant_id"])

    op.create_table(
        "care_packages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_care_packages_tenant_id", "care_packages", ["tenant_id"])

    op.create_table(
        "care_package_items",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("package_id", sa.String(length=36), sa.ForeignKey("care_packages.id"), nullable=False),
        sa.Column("item_id", sa.String(length=36), sa.ForeignKey("service_items.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )
    op.create_index("ix_care_package_items_tenant_id", "care_package_items", ["tenant_id"])

    op.create_table(
        "elder_packages",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("elder_id", sa.String(length=36), sa.ForeignKey("elders.id"), nullable=False),
        sa.Column("package_id", sa.String(length=36), sa.ForeignKey("care_packages.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
    )
    op.create_index("ix_elder_packages_tenant_id", "elder_packages", ["tenant_id"])

    op.create_table(
        "care_tasks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("elder_id", sa.String(length=36), sa.ForeignKey("elders.id"), nullable=False),
        sa.Column("item_id", sa.String(length=36), sa.ForeignKey("service_items.id"), nullable=False),
        sa.Column("assigned_to", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("qr_scan_in", sa.Text(), nullable=False),
        sa.Column("qr_scan_out", sa.Text(), nullable=False),
        sa.Column("supervise_score", sa.Integer(), nullable=False),
    )
    op.create_index("ix_care_tasks_tenant_id", "care_tasks", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("care_tasks")
    op.drop_table("elder_packages")
    op.drop_table("care_package_items")
    op.drop_table("care_packages")
    op.drop_table("service_items")
