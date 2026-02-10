"""oa4 training

Revision ID: 2026021111
Revises: 2026021110
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021111"
down_revision = "2026021110"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("training_courses",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("title",sa.String(100),nullable=False),sa.Column("category",sa.String(30),nullable=False),sa.Column("required_score",sa.Integer(),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_training_courses_tenant_id","training_courses",["tenant_id"])
    op.create_table("training_records",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("course_id",sa.String(36),sa.ForeignKey("training_courses.id"),nullable=False),sa.Column("user_id",sa.String(36),sa.ForeignKey("users.id"),nullable=False),sa.Column("completed_on",sa.Date(),nullable=True),sa.Column("score",sa.Integer(),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_training_records_tenant_id","training_records",["tenant_id"])



def downgrade() -> None:
    op.drop_table("training_records")
    op.drop_table("training_courses")
