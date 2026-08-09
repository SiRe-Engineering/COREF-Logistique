"""Add technical-administration cancellation audit fields.

Revision ID: 0020
Revises: 0019
"""

from alembic import op
import sqlalchemy as sa


revision = "0020"
down_revision = "0019"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lots_beton",
        sa.Column("supprime", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "lots_beton",
        sa.Column("date_suppression", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "lots_beton",
        sa.Column("supprime_par", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "lots_beton",
        sa.Column("motif_suppression", sa.Text(), nullable=True),
    )

    op.add_column(
        "mouvements_stock",
        sa.Column("annule", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("date_annulation", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("annule_par", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("motif_annulation", sa.Text(), nullable=True),
    )

    op.create_index(
        "ix_lots_beton_supprime",
        "lots_beton",
        ["supprime"],
    )
    op.create_index(
        "ix_mouvements_stock_annule",
        "mouvements_stock",
        ["annule"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_stock_annule",
        table_name="mouvements_stock",
    )
    op.drop_index(
        "ix_lots_beton_supprime",
        table_name="lots_beton",
    )

    op.drop_column("mouvements_stock", "motif_annulation")
    op.drop_column("mouvements_stock", "annule_par")
    op.drop_column("mouvements_stock", "date_annulation")
    op.drop_column("mouvements_stock", "annule")

    op.drop_column("lots_beton", "motif_suppression")
    op.drop_column("lots_beton", "supprime_par")
    op.drop_column("lots_beton", "date_suppression")
    op.drop_column("lots_beton", "supprime")
