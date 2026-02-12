"""shop inventory and order flow

Revision ID: 2026021117
Revises: 2026021116
Create Date: 2026-02-13
"""

from alembic import op
import sqlalchemy as sa


revision = "2026021117"
down_revision = "2026021116"
branch_labels = None
depends_on = None


def _uuid_col(name: str, nullable: bool = False):
    return sa.Column(name, sa.String(length=36), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "shop_categories",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("name_zh", sa.String(length=80), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="enabled"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_shop_categories_tenant_id", "shop_categories", ["tenant_id"])

    op.create_table(
        "shop_spu",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("category_id"),
        sa.Column("name_zh", sa.String(length=120), nullable=False),
        sa.Column("subtitle_zh", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("description_zh", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["category_id"], ["shop_categories.id"]),
    )
    op.create_index("ix_shop_spu_tenant_id", "shop_spu", ["tenant_id"])

    op.create_table(
        "shop_sku",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("spu_id"),
        sa.Column("sku_name_zh", sa.String(length=120), nullable=False),
        sa.Column("sku_code", sa.String(length=50), nullable=False),
        sa.Column("sale_price", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("warning_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reserved_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="on_shelf"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["spu_id"], ["shop_spu.id"]),
    )
    op.create_index("ix_shop_sku_tenant_id", "shop_sku", ["tenant_id"])

    op.create_table(
        "inventory_ledger",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("sku_id"),
        sa.Column("change_type", sa.String(length=20), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("before_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("after_stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("remark", sa.String(length=255), nullable=False, server_default=""),
        _uuid_col("related_order_id", nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sku_id"], ["shop_sku.id"]),
    )
    op.create_index("ix_inventory_ledger_tenant_id", "inventory_ledger", ["tenant_id"])

    op.create_table(
        "inventory_reservations",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("sku_id"),
        _uuid_col("order_id"),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="reserved"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sku_id"], ["shop_sku.id"]),
    )
    op.create_index("ix_inventory_reservations_tenant_id", "inventory_reservations", ["tenant_id"])

    op.create_table(
        "account_balances",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("elder_id"),
        sa.Column("balance", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["elder_id"], ["elders.id"]),
    )
    op.create_index("ix_account_balances_tenant_id", "account_balances", ["tenant_id"])

    op.create_table(
        "account_ledger",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("elder_id"),
        _uuid_col("order_id", nullable=True),
        sa.Column("biz_type", sa.String(length=30), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("direction", sa.String(length=10), nullable=False, server_default="debit"),
        sa.Column("balance_after", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("remark", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["elder_id"], ["elders.id"]),
    )
    op.create_index("ix_account_ledger_tenant_id", "account_ledger", ["tenant_id"])

    op.create_table(
        "shop_orders",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("elder_id"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="created"),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("paid_amount", sa.Numeric(10, 2), nullable=False, server_default="0"),
        sa.Column("cancel_reason", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["elder_id"], ["elders.id"]),
    )
    op.create_index("ix_shop_orders_tenant_id", "shop_orders", ["tenant_id"])

    op.create_table(
        "shop_order_items",
        _uuid_col("id"),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        _uuid_col("order_id"),
        _uuid_col("sku_id"),
        sa.Column("sku_name_zh", sa.String(length=120), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["order_id"], ["shop_orders.id"]),
        sa.ForeignKeyConstraint(["sku_id"], ["shop_sku.id"]),
    )
    op.create_index("ix_shop_order_items_tenant_id", "shop_order_items", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_shop_order_items_tenant_id", table_name="shop_order_items")
    op.drop_table("shop_order_items")
    op.drop_index("ix_shop_orders_tenant_id", table_name="shop_orders")
    op.drop_table("shop_orders")
    op.drop_index("ix_account_ledger_tenant_id", table_name="account_ledger")
    op.drop_table("account_ledger")
    op.drop_index("ix_account_balances_tenant_id", table_name="account_balances")
    op.drop_table("account_balances")
    op.drop_index("ix_inventory_reservations_tenant_id", table_name="inventory_reservations")
    op.drop_table("inventory_reservations")
    op.drop_index("ix_inventory_ledger_tenant_id", table_name="inventory_ledger")
    op.drop_table("inventory_ledger")
    op.drop_index("ix_shop_sku_tenant_id", table_name="shop_sku")
    op.drop_table("shop_sku")
    op.drop_index("ix_shop_spu_tenant_id", table_name="shop_spu")
    op.drop_table("shop_spu")
    op.drop_index("ix_shop_categories_tenant_id", table_name="shop_categories")
    op.drop_table("shop_categories")
