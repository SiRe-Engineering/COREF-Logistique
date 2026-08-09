"""Add preparation replacement proposal workflow.

Revision ID: 0019
Revises: 0018
"""

from alembic import op
import sqlalchemy as sa

revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_lignes_preparation_statut_execution",
        "lignes_preparation",
        type_="check",
    )

    op.add_column(
        "lignes_preparation",
        sa.Column(
            "article_remplacement_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "lot_remplacement_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "emplacement_remplacement_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "quantite_remplacement",
            sa.Numeric(precision=14, scale=3),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "commentaire_remplacement",
            sa.Text(),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column("propose_par", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "date_proposition_remplacement",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "decision_remplacement",
            sa.String(length=20),
            nullable=True,
        ),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column("decision_par", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column("commentaire_decision", sa.Text(), nullable=True),
    )
    op.add_column(
        "lignes_preparation",
        sa.Column(
            "date_decision_remplacement",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_lignes_preparation_article_remplacement",
        "lignes_preparation",
        "articles",
        ["article_remplacement_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_lignes_preparation_lot_remplacement",
        "lignes_preparation",
        "lots_beton",
        ["lot_remplacement_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_lignes_preparation_emplacement_remplacement",
        "lignes_preparation",
        "emplacements",
        ["emplacement_remplacement_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_index(
        "ix_lignes_preparation_article_remplacement_id",
        "lignes_preparation",
        ["article_remplacement_id"],
    )
    op.create_index(
        "ix_lignes_preparation_emplacement_remplacement_id",
        "lignes_preparation",
        ["emplacement_remplacement_id"],
    )

    op.create_check_constraint(
        "ck_lignes_preparation_quantite_remplacement_positive",
        "lignes_preparation",
        (
            "quantite_remplacement IS NULL "
            "OR quantite_remplacement > 0"
        ),
    )
    op.create_check_constraint(
        "ck_lignes_preparation_decision_remplacement",
        "lignes_preparation",
        (
            "decision_remplacement IS NULL "
            "OR decision_remplacement IN ('ACCEPTEE', 'REFUSEE')"
        ),
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
            "'REMPLACEMENT_PROPOSE', "
            "'REMPLACEMENT_ACCEPTE', "
            "'REMPLACEMENT_REFUSE', "
            "'EXPEDIEE'"
            ")"
        ),
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_lignes_preparation_statut_execution",
        "lignes_preparation",
        type_="check",
    )
    op.drop_constraint(
        "ck_lignes_preparation_decision_remplacement",
        "lignes_preparation",
        type_="check",
    )
    op.drop_constraint(
        "ck_lignes_preparation_quantite_remplacement_positive",
        "lignes_preparation",
        type_="check",
    )
    op.drop_index(
        "ix_lignes_preparation_emplacement_remplacement_id",
        table_name="lignes_preparation",
    )
    op.drop_index(
        "ix_lignes_preparation_article_remplacement_id",
        table_name="lignes_preparation",
    )
    op.drop_constraint(
        "fk_lignes_preparation_emplacement_remplacement",
        "lignes_preparation",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_lignes_preparation_lot_remplacement",
        "lignes_preparation",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_lignes_preparation_article_remplacement",
        "lignes_preparation",
        type_="foreignkey",
    )

    for column in (
        "date_decision_remplacement",
        "commentaire_decision",
        "decision_par",
        "decision_remplacement",
        "date_proposition_remplacement",
        "propose_par",
        "commentaire_remplacement",
        "quantite_remplacement",
        "emplacement_remplacement_id",
        "lot_remplacement_id",
        "article_remplacement_id",
    ):
        op.drop_column("lignes_preparation", column)

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
