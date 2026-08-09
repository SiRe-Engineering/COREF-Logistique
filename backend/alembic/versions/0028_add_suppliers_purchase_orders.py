"""Add suppliers and purchase orders.

Revision ID: 0028
Revises: 0027
"""

from alembic import op
import sqlalchemy as sa

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS commande_achat_reference_seq START 1")

    op.create_table(
        "fournisseurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(30), nullable=False),
        sa.Column("raison_sociale", sa.String(180), nullable=False),
        sa.Column("contact", sa.String(150), nullable=True),
        sa.Column("email", sa.String(180), nullable=True),
        sa.Column("telephone", sa.String(60), nullable=True),
        sa.Column("adresse", sa.Text(), nullable=True),
        sa.Column("conditions_paiement", sa.String(120), nullable=True),
        sa.Column("delai_habituel_jours", sa.Integer(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modification", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_fournisseurs_raison_sociale", "fournisseurs", ["raison_sociale"])

    op.create_table(
        "articles_fournisseurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("fournisseur_id", sa.Integer(), sa.ForeignKey("fournisseurs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reference_fournisseur", sa.String(120), nullable=True),
        sa.Column("prix_unitaire_ht", sa.Numeric(14,4), nullable=True),
        sa.Column("delai_jours", sa.Integer(), nullable=True),
        sa.Column("minimum_commande", sa.Numeric(14,3), nullable=True),
        sa.Column("fournisseur_prefere", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("date_maj_prix", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("article_id", "fournisseur_id", name="uq_article_fournisseur"),
    )

    op.create_table(
        "commandes_achat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(30), nullable=False, server_default=sa.text(
            "'CMD-' || lpad(nextval('commande_achat_reference_seq')::text, 6, '0')"
        )),
        sa.Column("fournisseur_id", sa.Integer(), sa.ForeignKey("fournisseurs.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("statut", sa.String(35), nullable=False, server_default="BROUILLON"),
        sa.Column("reference_fournisseur", sa.String(120), nullable=True),
        sa.Column("date_commande", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_livraison_prevue", sa.Date(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("cree_par", sa.String(150), nullable=True),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modification", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("reference"),
    )
    op.create_index("ix_commandes_achat_statut", "commandes_achat", ["statut"])
    op.create_index("ix_commandes_achat_fournisseur", "commandes_achat", ["fournisseur_id"])

    op.create_table(
        "lignes_commandes_achat",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commande_id", sa.Integer(), sa.ForeignKey("commandes_achat.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("besoin_reapprovisionnement_id", sa.Integer(), sa.ForeignKey("besoins_reapprovisionnement.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference_fournisseur", sa.String(120), nullable=True),
        sa.Column("quantite_commandee", sa.Numeric(14,3), nullable=False),
        sa.Column("quantite_recue", sa.Numeric(14,3), nullable=False, server_default="0"),
        sa.Column("prix_unitaire_ht", sa.Numeric(14,4), nullable=False),
        sa.UniqueConstraint("commande_id", "article_id", "besoin_reapprovisionnement_id", name="uq_commande_article_besoin"),
    )
    op.create_index("ix_lignes_commandes_commande", "lignes_commandes_achat", ["commande_id"])

    op.add_column("mouvements_stock", sa.Column("ligne_commande_achat_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_mouvements_ligne_commande_achat",
        "mouvements_stock", "lignes_commandes_achat",
        ["ligne_commande_achat_id"], ["id"], ondelete="RESTRICT",
    )
    op.create_index("ix_mouvements_ligne_commande_achat", "mouvements_stock", ["ligne_commande_achat_id"])


def downgrade() -> None:
    op.drop_index("ix_mouvements_ligne_commande_achat", table_name="mouvements_stock")
    op.drop_constraint("fk_mouvements_ligne_commande_achat", "mouvements_stock", type_="foreignkey")
    op.drop_column("mouvements_stock", "ligne_commande_achat_id")
    op.drop_index("ix_lignes_commandes_commande", table_name="lignes_commandes_achat")
    op.drop_table("lignes_commandes_achat")
    op.drop_index("ix_commandes_achat_fournisseur", table_name="commandes_achat")
    op.drop_index("ix_commandes_achat_statut", table_name="commandes_achat")
    op.drop_table("commandes_achat")
    op.drop_table("articles_fournisseurs")
    op.drop_index("ix_fournisseurs_raison_sociale", table_name="fournisseurs")
    op.drop_table("fournisseurs")
    op.execute("DROP SEQUENCE IF EXISTS commande_achat_reference_seq")
