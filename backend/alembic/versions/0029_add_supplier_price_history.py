"""Add supplier price history.

Revision ID: 0029
Revises: 0028
"""

from alembic import op
import sqlalchemy as sa


revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "historique_prix_fournisseurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_fournisseur_id",
            sa.Integer(),
            sa.ForeignKey(
                "articles_fournisseurs.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column("prix_unitaire_ht", sa.Numeric(14, 4), nullable=False),
        sa.Column(
            "date_effet",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("modifie_par", sa.String(length=150), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
    )
    op.create_index(
        "ix_historique_prix_article_fournisseur",
        "historique_prix_fournisseurs",
        ["article_fournisseur_id", "date_effet"],
    )

    # Seed the history with prices already entered in Lot M.
    op.execute(
        """
        INSERT INTO historique_prix_fournisseurs
            (article_fournisseur_id, prix_unitaire_ht, date_effet)
        SELECT
            id,
            prix_unitaire_ht,
            COALESCE(date_maj_prix, NOW())
        FROM articles_fournisseurs
        WHERE prix_unitaire_ht IS NOT NULL
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_historique_prix_article_fournisseur",
        table_name="historique_prix_fournisseurs",
    )
    op.drop_table("historique_prix_fournisseurs")
