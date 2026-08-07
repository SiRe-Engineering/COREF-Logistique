"""Add monthly stock valuation snapshots.

Revision ID: 0025
Revises: 0024
"""

from alembic import op
import sqlalchemy as sa


revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "snapshots_valorisation_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mois", sa.Date(), nullable=False),
        sa.Column(
            "valeur_physique",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "valeur_reservee",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "valeur_disponible",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "date_mise_a_jour",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint(
            "mois",
            name="uq_snapshots_valorisation_stock_mois",
        ),
    )
    op.create_index(
        "ix_snapshots_valorisation_stock_mois",
        "snapshots_valorisation_stock",
        ["mois"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_snapshots_valorisation_stock_mois",
        table_name="snapshots_valorisation_stock",
    )
    op.drop_table("snapshots_valorisation_stock")
