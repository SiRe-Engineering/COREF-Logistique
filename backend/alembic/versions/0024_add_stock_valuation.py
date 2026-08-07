"""Add weighted-average stock valuation.

Revision ID: 0024
Revises: 0023
"""

from alembic import op
import sqlalchemy as sa


revision = "0024"
down_revision = "0023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column(
            "cout_unitaire_moyen",
            sa.Numeric(14, 4),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "dernier_prix_achat",
            sa.Numeric(14, 4),
            nullable=True,
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "date_maj_cout",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.create_check_constraint(
        "ck_articles_cout_unitaire_moyen_positif",
        "articles",
        "cout_unitaire_moyen >= 0",
    )
    op.create_check_constraint(
        "ck_articles_dernier_prix_achat_positif",
        "articles",
        "dernier_prix_achat IS NULL OR dernier_prix_achat >= 0",
    )

    op.add_column(
        "mouvements_stock",
        sa.Column(
            "prix_unitaire_ht",
            sa.Numeric(14, 4),
            nullable=True,
        ),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column(
            "cout_unitaire_applique",
            sa.Numeric(14, 4),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column(
            "valeur_mouvement",
            sa.Numeric(18, 2),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("mouvements_stock", "valeur_mouvement")
    op.drop_column("mouvements_stock", "cout_unitaire_applique")
    op.drop_column("mouvements_stock", "prix_unitaire_ht")

    op.drop_constraint(
        "ck_articles_dernier_prix_achat_positif",
        "articles",
        type_="check",
    )
    op.drop_constraint(
        "ck_articles_cout_unitaire_moyen_positif",
        "articles",
        type_="check",
    )
    op.drop_column("articles", "date_maj_cout")
    op.drop_column("articles", "dernier_prix_achat")
    op.drop_column("articles", "cout_unitaire_moyen")
