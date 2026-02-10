"""m6 health

Revision ID: 2026021106
Revises: 2026021105
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021106"
down_revision = "2026021105"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("vital_sign_records",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("recorded_at",sa.DateTime(),nullable=False),sa.Column("temperature",sa.Numeric(4,1),nullable=False),sa.Column("systolic",sa.Integer(),nullable=False),sa.Column("diastolic",sa.Integer(),nullable=False),sa.Column("pulse",sa.Integer(),nullable=False));op.create_index("ix_vital_sign_records_tenant_id","vital_sign_records",["tenant_id"])
    op.create_table("health_assessments",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("assessed_on",sa.Date(),nullable=False),sa.Column("adl_score",sa.Integer(),nullable=False),sa.Column("mmse_score",sa.Integer(),nullable=False),sa.Column("risk_level",sa.String(20),nullable=False));op.create_index("ix_health_assessments_tenant_id","health_assessments",["tenant_id"])



def downgrade() -> None:
    op.drop_table("health_assessments")
    op.drop_table("vital_sign_records")
