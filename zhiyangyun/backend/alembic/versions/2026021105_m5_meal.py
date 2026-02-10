"""m5 meal

Revision ID: 2026021105
Revises: 2026021104
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021105"
down_revision = "2026021104"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("meal_plans",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("name",sa.String(100),nullable=False),sa.Column("plan_date",sa.Date(),nullable=False),sa.Column("meal_type",sa.String(20),nullable=False),sa.Column("nutrition_tag",sa.String(50),nullable=False),sa.Column("note",sa.Text(),nullable=False));op.create_index("ix_meal_plans_tenant_id","meal_plans",["tenant_id"])
    op.create_table("meal_orders",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("plan_id",sa.String(36),sa.ForeignKey("meal_plans.id"),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_meal_orders_tenant_id","meal_orders",["tenant_id"])



def downgrade() -> None:
    op.drop_table("meal_orders")
    op.drop_table("meal_plans")
