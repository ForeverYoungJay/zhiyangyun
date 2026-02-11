"""linkage enhance

Revision ID: 2026021115
Revises: 2026021114
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021115"
down_revision = "2026021114"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "family_care_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("elder_id", sa.String(36), sa.ForeignKey("elders.id"), nullable=False),
        sa.Column("task_id", sa.String(36), sa.ForeignKey("care_tasks.id"), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_family_care_records_tenant_id", "family_care_records", ["tenant_id"])

    op.create_table(
        "family_surveys",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("elder_id", sa.String(36), sa.ForeignKey("elders.id"), nullable=False),
        sa.Column("family_id", sa.String(36), sa.ForeignKey("family_accounts.id"), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_family_surveys_tenant_id", "family_surveys", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("family_surveys")
    op.drop_table("family_care_records")
