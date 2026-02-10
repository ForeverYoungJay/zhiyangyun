"""oa2 approval

Revision ID: 2026021109
Revises: 2026021108
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021109"
down_revision = "2026021108"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("approval_requests",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("module",sa.String(30),nullable=False),sa.Column("biz_id",sa.String(36),nullable=False),sa.Column("applicant_id",sa.String(36),sa.ForeignKey("users.id"),nullable=False),sa.Column("approver_id",sa.String(36),sa.ForeignKey("users.id"),nullable=True),sa.Column("status",sa.String(20),nullable=False),sa.Column("note",sa.Text(),nullable=False));op.create_index("ix_approval_requests_tenant_id","approval_requests",["tenant_id"])



def downgrade() -> None:
    op.drop_table("approval_requests")
