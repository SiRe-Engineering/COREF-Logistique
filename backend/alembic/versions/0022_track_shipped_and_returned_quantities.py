"""Track shipped and returned quantities on preparation lines.

Revision ID: 0022
Revises: 0021
"""

from alembic import op
import sqlalchemy as sa


revision = "0022"
down_revision = "0021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "quantite_expediee",
            sa.Numeric(14, 3),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "quantite_retournee",
            sa.Numeric(14, 3),
            nullable=False,
            server_default="0",
        ),
    )

    # Recover the shipped quantity for already shipped preparations.
    op.execute(
        """
        UPDATE lignes_preparation AS ligne
        SET quantite_expediee = ligne.quantite_preparee
        FROM preparations AS preparation
        WHERE preparation.id = ligne.preparation_id
          AND preparation.statut = 'EXPEDIEE'
        """
    )

    op.create_check_constraint(
        "ck_lignes_preparation_quantite_expediee_positive",
        "lignes_preparation",
        "quantite_expediee >= 0",
    )
    op.create_check_constraint(
        "ck_lignes_preparation_quantite_retournee_positive",
        "lignes_preparation",
        "quantite_retournee >= 0",
    )
    op.create_check_constraint(
        "ck_lignes_preparation_retour_inferieur_expedition",
        "lignes_preparation",
        "quantite_retournee <= quantite_expediee",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_lignes_preparation_retour_inferieur_expedition",
        "lignes_preparation",
        type_="check",
    )
    op.drop_constraint(
        "ck_lignes_preparation_quantite_retournee_positive",
        "lignes_preparation",
        type_="check",
    )
    op.drop_constraint(
        "ck_lignes_preparation_quantite_expediee_positive",
        "lignes_preparation",
        type_="check",
    )
    op.drop_column("lignes_preparation", "quantite_retournee")
    op.drop_column("lignes_preparation", "quantite_expediee")
