"""Indeks yaratish: tashqi kalitlar va mahsulot nomi bo'yicha qidiruv uchun

Revision ID: 0003
Revises: 0002
"""
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(op.f("ix_orders_user_id"), "orders", ["user_id"])
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"])
    op.create_index(op.f("ix_order_items_product_id"), "order_items", ["product_id"])
    op.create_index(op.f("ix_products_name"), "products", ["name"])


def downgrade() -> None:
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_order_items_product_id"), table_name="order_items")
    op.drop_index(op.f("ix_order_items_order_id"), table_name="order_items")
    op.drop_index(op.f("ix_orders_user_id"), table_name="orders")
