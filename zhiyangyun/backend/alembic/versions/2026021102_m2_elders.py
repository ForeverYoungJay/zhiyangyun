"""m2 elders lifecycle

Revision ID: 2026021102
Revises: 2026021101
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa

revision = "2026021102"
down_revision = "2026021101"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "crm_leads",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("source_channel", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
    )
    op.create_index("ix_crm_leads_tenant_id", "crm_leads", ["tenant_id"])

    op.create_table(
        "elders",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("lead_id", sa.String(length=36), sa.ForeignKey("crm_leads.id"), nullable=True),
        sa.Column("elder_no", sa.String(length=30), nullable=False, unique=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("gender", sa.String(length=10), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("id_card", sa.String(length=30), nullable=False),
        sa.Column("care_level", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("admission_date", sa.Date(), nullable=True),
        sa.Column("discharge_date", sa.Date(), nullable=True),
        sa.Column("building_id", sa.String(length=36), sa.ForeignKey("buildings.id"), nullable=True),
        sa.Column("floor_id", sa.String(length=36), sa.ForeignKey("floors.id"), nullable=True),
        sa.Column("room_id", sa.String(length=36), sa.ForeignKey("rooms.id"), nullable=True),
        sa.Column("bed_id", sa.String(length=36), sa.ForeignKey("beds.id"), nullable=True),
    )
    op.create_index("ix_elders_tenant_id", "elders", ["tenant_id"])

    op.create_table(
        "elder_change_logs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("elder_id", sa.String(length=36), sa.ForeignKey("elders.id"), nullable=False),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("detail", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_elder_change_logs_tenant_id", "elder_change_logs", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("elder_change_logs")
    op.drop_table("elders")
    op.drop_table("crm_leads")
