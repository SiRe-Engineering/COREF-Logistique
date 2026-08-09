"""Add equipment maintenance tracking.

Revision ID: 0036
Revises: 0035
"""
from alembic import op
import sqlalchemy as sa

revision="0036"
down_revision="0035"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "interventions_materiel",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("reference",sa.String(30),nullable=False,unique=True),
        sa.Column("materiel_id",sa.Integer(),sa.ForeignKey("materiels.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("type_intervention",sa.String(40),nullable=False),
        sa.Column("statut",sa.String(30),nullable=False),
        sa.Column("date_signalement",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("date_planifiee",sa.Date(),nullable=True),
        sa.Column("date_debut",sa.DateTime(timezone=True),nullable=True),
        sa.Column("date_fin",sa.DateTime(timezone=True),nullable=True),
        sa.Column("description",sa.Text(),nullable=False),
        sa.Column("diagnostic",sa.Text(),nullable=True),
        sa.Column("action_realisee",sa.Text(),nullable=True),
        sa.Column("prestataire",sa.String(180),nullable=True),
        sa.Column("cout_ht",sa.Numeric(14,2),nullable=True),
        sa.Column("prochain_controle",sa.Date(),nullable=True),
        sa.Column("cree_par",sa.String(150),nullable=True),
    )
    op.create_index("ix_interventions_materiel_materiel","interventions_materiel",["materiel_id"])
    op.create_index("ix_interventions_materiel_statut","interventions_materiel",["statut"])
    op.create_index("ix_interventions_materiel_date_planifiee","interventions_materiel",["date_planifiee"])

def downgrade():
    op.drop_index("ix_interventions_materiel_date_planifiee",table_name="interventions_materiel")
    op.drop_index("ix_interventions_materiel_statut",table_name="interventions_materiel")
    op.drop_index("ix_interventions_materiel_materiel",table_name="interventions_materiel")
    op.drop_table("interventions_materiel")
