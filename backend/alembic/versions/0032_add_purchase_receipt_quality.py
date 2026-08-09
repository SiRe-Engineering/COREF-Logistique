"""Add purchase receipt quality controls.

Revision ID: 0032
Revises: 0031
"""
from alembic import op
import sqlalchemy as sa

revision = "0032"
down_revision = "0031"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "receptions_achat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "commande_id",
            sa.Integer(),
            sa.ForeignKey("commandes_achat.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "ligne_commande_id",
            sa.Integer(),
            sa.ForeignKey("lignes_commandes_achat.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "lot_beton_id",
            sa.Integer(),
            sa.ForeignKey("lots_beton.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("quantite", sa.Numeric(14, 3), nullable=False),
        sa.Column("bon_livraison_reference", sa.String(120), nullable=True),
        sa.Column("conformite_visuelle", sa.String(30), nullable=False),
        sa.Column("reserve_commentaire", sa.Text(), nullable=True),
        sa.Column("commentaire_qualite", sa.Text(), nullable=True),
        sa.Column("fds_presente", sa.Boolean(), nullable=True),
        sa.Column("statut_qualite", sa.String(30), nullable=False),
        sa.Column("receptionne_par", sa.String(150), nullable=True),
        sa.Column(
            "date_reception",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_receptions_achat_commande",
        "receptions_achat",
        ["commande_id"],
    )
    op.create_index(
        "ix_receptions_achat_ligne",
        "receptions_achat",
        ["ligne_commande_id"],
    )
    op.create_index(
        "ix_receptions_achat_statut_qualite",
        "receptions_achat",
        ["statut_qualite"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_receptions_achat_statut_qualite",
        table_name="receptions_achat",
    )
    op.drop_index(
        "ix_receptions_achat_ligne",
        table_name="receptions_achat",
    )
    op.drop_index(
        "ix_receptions_achat_commande",
        table_name="receptions_achat",
    )
    op.drop_table("receptions_achat")
