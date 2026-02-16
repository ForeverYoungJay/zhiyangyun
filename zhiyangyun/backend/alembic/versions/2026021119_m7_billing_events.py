"""m7 billing events

Revision ID: 2026021119
Revises: 2026021118
Create Date: 2026-02-16
"""

from alembic import op
import sqlalchemy as sa


revision = "2026021119"
down_revision = "2026021118"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "billing_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("invoice_id", sa.String(36), sa.ForeignKey("billing_invoices.id"), nullable=False),
        sa.Column("event_type", sa.String(30), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_billing_events_tenant_id", "billing_events", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_billing_events_tenant_id", table_name="billing_events")
    op.drop_table("billing_events")
