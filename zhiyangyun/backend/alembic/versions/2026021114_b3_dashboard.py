"""b3 dashboard

Revision ID: 2026021114
Revises: 2026021113
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021114"
down_revision = "2026021113"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("dashboard_metrics",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("metric_date",sa.Date(),nullable=False),sa.Column("occupancy_rate",sa.Numeric(5,2),nullable=False),sa.Column("revenue",sa.Numeric(10,2),nullable=False),sa.Column("alerts",sa.Integer(),nullable=False));op.create_index("ix_dashboard_metrics_tenant_id","dashboard_metrics",["tenant_id"])



def downgrade() -> None:
    op.drop_table("dashboard_metrics")
