"""oa1 upgrade

Revision ID: 2026021120
Revises: 2026021119
Create Date: 2026-02-24
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2026021120"
down_revision = "2026021119"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shift_templates", sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"))
    op.execute("UPDATE shift_assignments SET status='draft' WHERE status='assigned'")


def downgrade() -> None:
    op.execute("UPDATE shift_assignments SET status='assigned' WHERE status='draft'")
    op.drop_column("shift_templates", "status")
