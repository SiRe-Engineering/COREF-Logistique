"""Add equipment loans.

Revision ID: 0035
Revises: 0034
"""
from alembic import op
import sqlalchemy as sa

revision="0035"
down_revision="0034"
branch_labels=None
depends_on=None

def upgrade():
    op.create_table(
        "prets_materiel",
        sa.Column("id",sa.Integer(),primary_key=True),
        sa.Column("reference",sa.String(30),nullable=False,unique=True),
        sa.Column("materiel_id",sa.Integer(),sa.ForeignKey("materiels.id",ondelete="RESTRICT"),nullable=False),
        sa.Column("emprunteur_id",sa.Integer(),sa.ForeignKey("utilisateurs.id",ondelete="SET NULL"),nullable=True),
        sa.Column("affaire_id",sa.Integer(),sa.ForeignKey("affaires.id",ondelete="SET NULL"),nullable=True),
        sa.Column("site_zone",sa.String(180),nullable=True),
        sa.Column("date_sortie",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column("date_retour_prevue",sa.Date(),nullable=False),
        sa.Column("date_retour_reelle",sa.DateTime(timezone=True),nullable=True),
        sa.Column("etat_depart",sa.String(30),nullable=False),
        sa.Column("etat_retour",sa.String(30),nullable=True),
        sa.Column("emplacement_depart_id",sa.Integer(),sa.ForeignKey("emplacements.id",ondelete="SET NULL"),nullable=True),
        sa.Column("emplacement_retour_id",sa.Integer(),sa.ForeignKey("emplacements.id",ondelete="SET NULL"),nullable=True),
        sa.Column("commentaire_sortie",sa.Text(),nullable=True),
        sa.Column("commentaire_retour",sa.Text(),nullable=True),
        sa.Column("cree_par",sa.String(150),nullable=True),
    )
    op.create_index("ix_prets_materiel_materiel","prets_materiel",["materiel_id"])
    op.create_index("ix_prets_materiel_retour_prevu","prets_materiel",["date_retour_prevue"])
    op.create_index(
        "uq_prets_materiel_actif",
        "prets_materiel",
        ["materiel_id"],
        unique=True,
        postgresql_where=sa.text("date_retour_reelle IS NULL"),
    )

def downgrade():
    op.drop_index("uq_prets_materiel_actif",table_name="prets_materiel")
    op.drop_index("ix_prets_materiel_retour_prevu",table_name="prets_materiel")
    op.drop_index("ix_prets_materiel_materiel",table_name="prets_materiel")
    op.drop_table("prets_materiel")
