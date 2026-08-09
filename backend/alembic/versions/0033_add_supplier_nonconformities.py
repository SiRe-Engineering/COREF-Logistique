"""Add supplier non-conformities.

Revision ID: 0033
Revises: 0032
"""
from alembic import op
import sqlalchemy as sa

revision="0033"
down_revision="0032"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "non_conformites_fournisseurs",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("reference",sa.String(30),nullable=False,unique=True),
        sa.Column("reception_id",sa.Integer(),sa.ForeignKey("receptions_achat.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("quantite_concernee",sa.Numeric(14,3),nullable=False),
        sa.Column("description",sa.Text(),nullable=False),
        sa.Column("decision",sa.String(40),nullable=True),
        sa.Column("responsable",sa.String(150),nullable=True),
        sa.Column("statut",sa.String(30),nullable=False,server_default="OUVERTE"),
        sa.Column("commentaire_traitement",sa.Text(),nullable=True),
        sa.Column("date_creation",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("date_cloture",sa.DateTime(timezone=True),nullable=True),
        sa.Column("cree_par",sa.String(150),nullable=True),
    )
    op.create_index("ix_ncf_reception","non_conformites_fournisseurs",["reception_id"])
    op.create_index("ix_ncf_statut","non_conformites_fournisseurs",["statut"])

def downgrade():
    op.drop_index("ix_ncf_statut",table_name="non_conformites_fournisseurs")
    op.drop_index("ix_ncf_reception",table_name="non_conformites_fournisseurs")
    op.drop_table("non_conformites_fournisseurs")
