"""b1 miniapp

Revision ID: 2026021112
Revises: 2026021111
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021112"
down_revision = "2026021111"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("miniapp_service_requests",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("request_type",sa.String(30),nullable=False),sa.Column("content",sa.String(255),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_miniapp_service_requests_tenant_id","miniapp_service_requests",["tenant_id"])



def downgrade() -> None:
    op.drop_table("miniapp_service_requests")
