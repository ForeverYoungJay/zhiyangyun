"""m6 health business upgrade

Revision ID: 2026021118
Revises: 2026021117
Create Date: 2026-02-15
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021118"
down_revision = "2026021117"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vital_sign_records", sa.Column("abnormal_level", sa.String(length=20), nullable=False, server_default="normal"))
    op.add_column("vital_sign_records", sa.Column("abnormal_reason", sa.Text(), nullable=False, server_default=""))
    op.add_column("vital_sign_records", sa.Column("followup_task_id", sa.String(length=36), sa.ForeignKey("care_tasks.id"), nullable=True))

    op.add_column("health_assessments", sa.Column("status", sa.String(length=20), nullable=False, server_default="open"))
    op.add_column("health_assessments", sa.Column("followup_task_id", sa.String(length=36), sa.ForeignKey("care_tasks.id"), nullable=True))
    op.add_column("health_assessments", sa.Column("closed_at", sa.DateTime(), nullable=True))
    op.add_column("health_assessments", sa.Column("close_note", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("health_assessments", "close_note")
    op.drop_column("health_assessments", "closed_at")
    op.drop_column("health_assessments", "followup_task_id")
    op.drop_column("health_assessments", "status")

    op.drop_column("vital_sign_records", "followup_task_id")
    op.drop_column("vital_sign_records", "abnormal_reason")
    op.drop_column("vital_sign_records", "abnormal_level")
