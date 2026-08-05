"""Initial inventory schema.

Revision ID: 0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    movement_type = sa.Enum(
        "ENTRY", "EXIT", "TRANSFER", "ADJUSTMENT",
        name="movementtype"
    )
    movement_type.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(length=80), nullable=False),
        sa.Column("designation", sa.String(length=255), nullable=False),
        sa.Column("family", sa.String(length=120), nullable=True),
        sa.Column("subfamily", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=False, server_default="unité"),
        sa.Column("minimum_stock", sa.Numeric(12, 3), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_items_reference", "items", ["reference"], unique=True)
    op.create_index("ix_items_designation", "items", ["designation"], unique=False)

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_locations_code", "locations", ["code"], unique=True)

    op.create_table(
        "stock_movements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("items.id"), nullable=False),
        sa.Column("source_location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("destination_location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("movement_type", movement_type, nullable=False),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_stock_movements_item_id", "stock_movements", ["item_id"])


def downgrade() -> None:
    op.drop_table("stock_movements")
    op.drop_table("locations")
    op.drop_table("items")
    sa.Enum(name="movementtype").drop(op.get_bind(), checkfirst=True)
