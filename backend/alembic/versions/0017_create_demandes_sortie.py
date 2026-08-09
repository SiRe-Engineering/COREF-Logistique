"""Create stock issue approval requests.

Revision ID: 0017
Revises: 0016
"""

from alembic import op
import sqlalchemy as sa

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS demande_sortie_reference_seq START WITH 1"
    )

    op.create_table(
        "demandes_sortie",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'DS-' || lpad(nextval('demande_sortie_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column(
            "demandeur_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "validateur_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "lot_id",
            sa.Integer(),
            sa.ForeignKey("lots_beton.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "emplacement_source_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "affaire_id",
            sa.Integer(),
            sa.ForeignKey("affaires.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("quantite", sa.Numeric(14, 3), nullable=False),
        sa.Column("vehicule", sa.String(length=120), nullable=True),
        sa.Column("motif", sa.String(length=255), nullable=False),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column(
            "statut",
            sa.String(length=30),
            nullable=False,
            server_default="EN_ATTENTE",
        ),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_decision", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motif_refus", sa.Text(), nullable=True),
        sa.UniqueConstraint("reference", name="uq_demandes_sortie_reference"),
        sa.CheckConstraint(
            "quantite > 0",
            name="ck_demandes_sortie_quantite_positive",
        ),
    )

    op.create_index("ix_demandes_sortie_demandeur_id", "demandes_sortie", ["demandeur_id"])
    op.create_index("ix_demandes_sortie_validateur_id", "demandes_sortie", ["validateur_id"])
    op.create_index("ix_demandes_sortie_statut", "demandes_sortie", ["statut"])


def downgrade() -> None:
    op.drop_index("ix_demandes_sortie_statut", table_name="demandes_sortie")
    op.drop_index("ix_demandes_sortie_validateur_id", table_name="demandes_sortie")
    op.drop_index("ix_demandes_sortie_demandeur_id", table_name="demandes_sortie")
    op.drop_table("demandes_sortie")
    op.execute("DROP SEQUENCE IF EXISTS demande_sortie_reference_seq")
