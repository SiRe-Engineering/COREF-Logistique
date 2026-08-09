"""Inventaires avances et ecarts de stock.

Revision ID: 0038
Revises: 0037
"""
from alembic import op
import sqlalchemy as sa

revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "campagnes_inventaire_avance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(30), nullable=False, unique=True),
        sa.Column("libelle", sa.String(180), nullable=False),
        sa.Column("statut", sa.String(30), nullable=False, server_default="BROUILLON"),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("date_comptage", sa.Date(), nullable=True),
        sa.Column("date_validation", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cree_par", sa.String(150), nullable=True),
        sa.Column("valide_par", sa.String(150), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
    )
    op.create_table(
        "lignes_inventaire_avance",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campagne_id", sa.Integer(), sa.ForeignKey("campagnes_inventaire_avance.id", ondelete="CASCADE"), nullable=False),
        sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("emplacement_id", sa.Integer(), sa.ForeignKey("emplacements.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantite_theorique", sa.Numeric(14, 3), nullable=False),
        sa.Column("quantite_comptee", sa.Numeric(14, 3), nullable=True),
        sa.Column("prix_unitaire", sa.Numeric(14, 4), nullable=False, server_default="0"),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column("compte_par", sa.String(150), nullable=True),
        sa.Column("date_comptage", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("campagne_id", "article_id", "emplacement_id", name="uq_inventaire_avance_article_emplacement"),
    )
    op.create_index("ix_lignes_inventaire_avance_campagne", "lignes_inventaire_avance", ["campagne_id"])
    op.create_index("ix_lignes_inventaire_avance_article", "lignes_inventaire_avance", ["article_id"])

def downgrade():
    op.drop_index("ix_lignes_inventaire_avance_article", table_name="lignes_inventaire_avance")
    op.drop_index("ix_lignes_inventaire_avance_campagne", table_name="lignes_inventaire_avance")
    op.drop_table("lignes_inventaire_avance")
    op.drop_table("campagnes_inventaire_avance")
