"""oa3 notification

Revision ID: 2026021110
Revises: 2026021109
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021110"
down_revision = "2026021109"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("notification_messages",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("title",sa.String(100),nullable=False),sa.Column("content",sa.Text(),nullable=False),sa.Column("channel",sa.String(20),nullable=False),sa.Column("receiver_scope",sa.String(20),nullable=False),sa.Column("sent_at",sa.DateTime(),nullable=False));op.create_index("ix_notification_messages_tenant_id","notification_messages",["tenant_id"])



def downgrade() -> None:
    op.drop_table("notification_messages")
