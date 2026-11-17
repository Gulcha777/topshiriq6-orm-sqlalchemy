"""Yangi ustun qo'shish: users.phone

Revision ID: 0002
Revises: 0001
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=20), nullable=True))


def downgrade() -> None:
    # SQLite'da ustunni o'chirish uchun batch rejimi kerak
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("phone")
