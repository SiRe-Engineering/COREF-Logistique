"""Link stock movements to preparations and lines.

Revision ID: 0021
Revises: 0020
"""

from alembic import op
import sqlalchemy as sa


revision = "0021"
down_revision = "0020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "mouvements_stock",
        sa.Column(
            "preparation_id",
            sa.Integer(),
            sa.ForeignKey(
                "preparations.id",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column(
            "ligne_preparation_id",
            sa.Integer(),
            sa.ForeignKey(
                "lignes_preparation.id",
                ondelete="RESTRICT",
            ),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_mouvements_stock_preparation_id",
        "mouvements_stock",
        ["preparation_id"],
    )
    op.create_index(
        "ix_mouvements_stock_ligne_preparation_id",
        "mouvements_stock",
        ["ligne_preparation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_stock_ligne_preparation_id",
        table_name="mouvements_stock",
    )
    op.drop_index(
        "ix_mouvements_stock_preparation_id",
        table_name="mouvements_stock",
    )
    op.drop_column("mouvements_stock", "ligne_preparation_id")
    op.drop_column("mouvements_stock", "preparation_id")
