"""b2 family

Revision ID: 2026021113
Revises: 2026021112
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021113"
down_revision = "2026021112"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("family_accounts",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("elder_id",sa.String(36),sa.ForeignKey("elders.id"),nullable=False),sa.Column("name",sa.String(50),nullable=False),sa.Column("phone",sa.String(20),nullable=False),sa.Column("relation",sa.String(20),nullable=False));op.create_index("ix_family_accounts_tenant_id","family_accounts",["tenant_id"])
    op.create_table("family_visits",sa.Column("id",sa.String(36),primary_key=True),sa.Column("tenant_id",sa.String(36),nullable=False),sa.Column("family_id",sa.String(36),sa.ForeignKey("family_accounts.id"),nullable=False),sa.Column("visit_date",sa.Date(),nullable=False),sa.Column("status",sa.String(20),nullable=False));op.create_index("ix_family_visits_tenant_id","family_visits",["tenant_id"])



def downgrade() -> None:
    op.drop_table("family_visits")
    op.drop_table("family_accounts")
