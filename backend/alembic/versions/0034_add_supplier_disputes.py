"""Supplier returns, credits and replacements.

Revision ID: 0034
Revises: 0033
"""
from alembic import op
import sqlalchemy as sa
revision="0034"; down_revision="0033"; branch_labels=None; depends_on=None
def upgrade():
    op.create_table("litiges_fournisseurs",
      sa.Column("id",sa.Integer(),primary_key=True),
      sa.Column("reference",sa.String(30),nullable=False,unique=True),
      sa.Column("ncf_id",sa.Integer(),sa.ForeignKey("non_conformites_fournisseurs.id",ondelete="RESTRICT"),nullable=False,unique=True),
      sa.Column("type_traitement",sa.String(40),nullable=False),
      sa.Column("statut",sa.String(40),nullable=False),
      sa.Column("quantite_retour",sa.Numeric(14,3),nullable=True),
      sa.Column("emplacement_source_id",sa.Integer(),sa.ForeignKey("emplacements.id",ondelete="RESTRICT"),nullable=True),
      sa.Column("date_retour",sa.DateTime(timezone=True),nullable=True),
      sa.Column("mouvement_sortie_id",sa.Integer(),sa.ForeignKey("mouvements_stock.id",ondelete="SET NULL"),nullable=True),
      sa.Column("reference_avoir",sa.String(120),nullable=True),
      sa.Column("montant_avoir_ht",sa.Numeric(14,2),nullable=True),
      sa.Column("date_avoir",sa.Date(),nullable=True),
      sa.Column("reception_remplacement_id",sa.Integer(),sa.ForeignKey("receptions_achat.id",ondelete="SET NULL"),nullable=True),
      sa.Column("quantite_conforme_tri",sa.Numeric(14,3),nullable=True),
      sa.Column("quantite_rebut_tri",sa.Numeric(14,3),nullable=True),
      sa.Column("commentaire",sa.Text(),nullable=True),
      sa.Column("date_creation",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
      sa.Column("date_cloture",sa.DateTime(timezone=True),nullable=True),
      sa.Column("cree_par",sa.String(150),nullable=True))
    op.create_index("ix_litiges_statut","litiges_fournisseurs",["statut"])
def downgrade():
    op.drop_index("ix_litiges_statut",table_name="litiges_fournisseurs")
    op.drop_table("litiges_fournisseurs")
