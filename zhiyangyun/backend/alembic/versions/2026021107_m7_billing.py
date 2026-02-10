"""m7 billing

Revision ID: 2026021107
Revises: 2026021106
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021107"
down_revision = "2026021106"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("billing_items",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("item_name",sa.String(100),nullable=False),sa.Column("amount",sa.Numeric(10,2),nullable=False),sa.Column("charged_on",sa.Date(),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_billing_items_tenant_id","billing_items",["tenant_id"])
    op.create_table("billing_invoices",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("period_month",sa.String(7),nullable=False),sa.Column("total_amount",sa.Numeric(10,2),nullable=False),sa.Column("paid_amount",sa.Numeric(10,2),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_billing_invoices_tenant_id","billing_invoices",["tenant_id"])



def downgrade() -> None:
    op.drop_table("billing_invoices")
    op.drop_table("billing_items")
