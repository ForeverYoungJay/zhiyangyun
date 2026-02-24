"""oa2-oa4 business upgrade

Revision ID: 2026021121
Revises: 2026021120
Create Date: 2026-02-24
"""

from alembic import op
import sqlalchemy as sa


revision = "2026021121"
down_revision = "2026021120"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("approval_requests", sa.Column("cc_user_ids", sa.Text(), nullable=False, server_default=""))
    op.add_column("approval_requests", sa.Column("current_step", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("approval_requests", sa.Column("total_steps", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("approval_requests", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("approval_requests", sa.Column("rejected_at", sa.DateTime(), nullable=True))
    op.add_column("approval_requests", sa.Column("closed_at", sa.DateTime(), nullable=True))

    op.create_table(
        "approval_action_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("request_id", sa.String(36), sa.ForeignKey("approval_requests.id"), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("operator_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("note", sa.Text(), nullable=False, server_default=""),
        sa.Column("acted_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_approval_action_logs_tenant_id", "approval_action_logs", ["tenant_id"])

    op.add_column("notification_messages", sa.Column("target_user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("notification_messages", sa.Column("strategy", sa.String(30), nullable=False, server_default="immediate"))
    op.add_column("notification_messages", sa.Column("status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("notification_messages", sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("notification_messages", sa.Column("delivered_at", sa.DateTime(), nullable=True))

    op.add_column("training_courses", sa.Column("trainer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("training_courses", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("training_courses", sa.Column("end_date", sa.Date(), nullable=True))

    op.add_column("training_records", sa.Column("attendance_status", sa.String(20), nullable=False, server_default="unsigned"))
    op.add_column("training_records", sa.Column("attended_at", sa.DateTime(), nullable=True))
    op.add_column("training_records", sa.Column("exam_status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("training_records", sa.Column("assessed_at", sa.DateTime(), nullable=True))
    op.add_column("training_records", sa.Column("evaluator_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("training_records", sa.Column("remark", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("training_records", "remark")
    op.drop_column("training_records", "evaluator_id")
    op.drop_column("training_records", "assessed_at")
    op.drop_column("training_records", "exam_status")
    op.drop_column("training_records", "attended_at")
    op.drop_column("training_records", "attendance_status")

    op.drop_column("training_courses", "end_date")
    op.drop_column("training_courses", "start_date")
    op.drop_column("training_courses", "trainer_id")

    op.drop_column("notification_messages", "delivered_at")
    op.drop_column("notification_messages", "retry_count")
    op.drop_column("notification_messages", "status")
    op.drop_column("notification_messages", "strategy")
    op.drop_column("notification_messages", "target_user_id")

    op.drop_index("ix_approval_action_logs_tenant_id", table_name="approval_action_logs")
    op.drop_table("approval_action_logs")

    op.drop_column("approval_requests", "closed_at")
    op.drop_column("approval_requests", "rejected_at")
    op.drop_column("approval_requests", "approved_at")
    op.drop_column("approval_requests", "total_steps")
    op.drop_column("approval_requests", "current_step")
    op.drop_column("approval_requests", "cc_user_ids")
