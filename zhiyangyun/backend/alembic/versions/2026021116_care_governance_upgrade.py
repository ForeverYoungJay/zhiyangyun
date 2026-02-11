"""care governance upgrade

Revision ID: 2026021116
Revises: 2026021115
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021116"
down_revision = "2026021115"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("care_packages", sa.Column("default_months", sa.Integer(), nullable=False, server_default="6"))

    op.create_table(
        "care_package_assignments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("package_id", sa.String(36), sa.ForeignKey("care_packages.id"), nullable=False),
        sa.Column("caregiver_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("months", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
    )
    op.create_index("ix_care_package_assignments_tenant_id", "care_package_assignments", ["tenant_id"])

    op.add_column("care_tasks", sa.Column("package_assignment_id", sa.String(36), sa.ForeignKey("care_package_assignments.id"), nullable=True))
    op.add_column("care_tasks", sa.Column("task_type", sa.String(30), nullable=False, server_default="care"))
    op.add_column("care_tasks", sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("care_tasks", sa.Column("execution_seconds", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("care_tasks", sa.Column("issue_photo_urls", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("care_tasks", sa.Column("issue_description", sa.Text(), nullable=False, server_default=""))
    op.add_column("care_tasks", sa.Column("report_to_dean", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("care_tasks", sa.Column("dean_review_status", sa.String(20), nullable=False, server_default="pending"))
    op.add_column("care_tasks", sa.Column("dean_review_note", sa.Text(), nullable=False, server_default=""))
    op.add_column("care_tasks", sa.Column("dean_deduction", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "caregiver_performance",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("caregiver_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("last_deduction_at", sa.DateTime(), nullable=True),
        sa.Column("rotation_suggestion", sa.Text(), nullable=False, server_default=""),
    )
    op.create_index("ix_caregiver_performance_tenant_id", "caregiver_performance", ["tenant_id"])

    op.create_table(
        "task_dispatch_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("dispatcher_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("dispatch_type", sa.String(30), nullable=False, server_default="periodic"),
        sa.Column("frequency", sa.String(20), nullable=False, server_default="day"),
        sa.Column("custom_times", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_tasks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_task_dispatch_logs_tenant_id", "task_dispatch_logs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("task_dispatch_logs")
    op.drop_table("caregiver_performance")

    op.drop_column("care_tasks", "dean_deduction")
    op.drop_column("care_tasks", "dean_review_note")
    op.drop_column("care_tasks", "dean_review_status")
    op.drop_column("care_tasks", "report_to_dean")
    op.drop_column("care_tasks", "issue_description")
    op.drop_column("care_tasks", "issue_photo_urls")
    op.drop_column("care_tasks", "execution_seconds")
    op.drop_column("care_tasks", "created_by")
    op.drop_column("care_tasks", "task_type")
    op.drop_column("care_tasks", "package_assignment_id")

    op.drop_table("care_package_assignments")
    op.drop_column("care_packages", "default_months")
