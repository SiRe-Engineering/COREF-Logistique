"""Add minimal preparation-line execution statuses.

Revision ID: 0018
Revises: 0017
"""

from alembic import op
import sqlalchemy as sa

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "quantite_manquante",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column("motif_ecart", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "date_debut_preparation",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "date_fin_preparation",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE lignes_preparation
        SET statut = CASE
            WHEN statut = 'PREPAREE' THEN 'PREPAREE'
            WHEN statut = 'EXPEDIEE' THEN 'EXPEDIEE'
            ELSE 'A_PREPARER'
        END,
        quantite_manquante =
            GREATEST(quantite_demandee - quantite_preparee, 0)
        """
    )

    op.create_check_constraint(
        "ck_lignes_preparation_quantite_manquante_positive",
        "lignes_preparation",
        "quantite_manquante >= 0",
    )
    op.create_check_constraint(
        "ck_lignes_preparation_statut_execution",
        "lignes_preparation",
        (
            "statut IN ("
            "'A_PREPARER', "
            "'PREPAREE', "
            "'PARTIELLE', "
            "'INDISPONIBLE', "
            "'EXPEDIEE'"
            ")"
        ),
    )
    op.create_index(
        "ix_lignes_preparation_statut",
        "lignes_preparation",
        ["statut"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lignes_preparation_statut",
        table_name="lignes_preparation",
    )
    op.drop_constraint(
        "ck_lignes_preparation_statut_execution",
        "lignes_preparation",
        type_="check",
    )
    op.drop_constraint(
        "ck_lignes_preparation_quantite_manquante_positive",
        "lignes_preparation",
        type_="check",
    )
    op.drop_column("lignes_preparation", "date_fin_preparation")
    op.drop_column("lignes_preparation", "date_debut_preparation")
    op.drop_column("lignes_preparation", "motif_ecart")
    op.drop_column("lignes_preparation", "quantite_manquante")
