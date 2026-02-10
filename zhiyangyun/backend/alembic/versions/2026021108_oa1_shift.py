"""oa1 shift

Revision ID: 2026021108
Revises: 2026021107
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021108"
down_revision = "2026021107"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("shift_templates",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("name",sa.String(50),nullable=False),sa.Column("start_time",sa.String(5),nullable=False),sa.Column("end_time",sa.String(5),nullable=False));op.create_index("ix_shift_templates_tenant_id","shift_templates",["tenant_id"])
    op.create_table("shift_assignments",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("shift_id",sa.String(36),sa.ForeignKey("shift_templates.id"),nullable=False),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id"),nullable=False),sa.Column("duty_date",sa.Date(),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_shift_assignments_tenant_id","shift_assignments",["tenant_id"])



def downgrade() -> None:
    op.drop_table("shift_assignments")
    op.drop_table("shift_templates")
