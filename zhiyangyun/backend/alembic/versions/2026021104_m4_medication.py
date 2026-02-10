"""m4 medication

Revision ID: 2026021104
Revises: 2026021103
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021104"
down_revision = "2026021103"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("medication_orders",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("drug_name",sa.String(100),nullable=False),sa.Column("dosage",sa.String(50),nullable=False),sa.Column("frequency",sa.String(50),nullable=False),sa.Column("start_date",sa.Date(),nullable=False),sa.Column("end_date",sa.Date(),nullable=True),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_medication_orders_tenant_id","medication_orders",["tenant_id"])
    op.create_table("medication_executions",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("order_id",sa.String(36),sa.ForeignKey("medication_orders.id"),nullable=False),sa.Column("executed_at",sa.DateTime(),nullable=False),sa.Column("executor_id",sa.String(36),sa.ForeignKey("users.id"),nullable=True),sa.Column("result",sa.String(20),nullable=False),sa.Column("note",sa.Text(),nullable=False));op.create_index("ix_medication_executions_tenant_id","medication_executions",["tenant_id"])



def downgrade() -> None:
    op.drop_table("medication_executions")
    op.drop_table("medication_orders")
