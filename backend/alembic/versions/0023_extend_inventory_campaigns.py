"""Extend inventory campaigns and movement traceability.

Revision ID: 0023
Revises: 0022
"""

from alembic import op
import sqlalchemy as sa


revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "inventaires",
        sa.Column(
            "type",
            sa.String(length=30),
            nullable=False,
            server_default="EMPLACEMENT",
        ),
    )
    op.add_column(
        "inventaires",
        sa.Column(
            "famille_id",
            sa.Integer(),
            sa.ForeignKey("familles.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    op.add_column(
        "inventaires",
        sa.Column(
            "valide_par",
            sa.String(length=150),
            nullable=True,
        ),
    )
    op.alter_column(
        "inventaires",
        "emplacement_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_index(
        "ix_inventaires_type",
        "inventaires",
        ["type"],
    )
    op.create_index(
        "ix_inventaires_famille_id",
        "inventaires",
        ["famille_id"],
    )

    op.add_column(
        "lignes_inventaire",
        sa.Column(
            "emplacement_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    op.execute(
        """
        UPDATE lignes_inventaire AS ligne
        SET emplacement_id = inventaire.emplacement_id
        FROM inventaires AS inventaire
        WHERE inventaire.id = ligne.inventaire_id
        """
    )
    op.alter_column(
        "lignes_inventaire",
        "emplacement_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_constraint(
        "uq_lignes_inventaire_article_lot",
        "lignes_inventaire",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_lignes_inventaire_emplacement_article_lot",
        "lignes_inventaire",
        [
            "inventaire_id",
            "emplacement_id",
            "article_id",
            "lot_id",
        ],
    )
    op.create_index(
        "ix_lignes_inventaire_emplacement_id",
        "lignes_inventaire",
        ["emplacement_id"],
    )

    op.add_column(
        "mouvements_stock",
        sa.Column(
            "inventaire_id",
            sa.Integer(),
            sa.ForeignKey("inventaires.id", ondelete="RESTRICT"),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_mouvements_stock_inventaire_id",
        "mouvements_stock",
        ["inventaire_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_stock_inventaire_id",
        table_name="mouvements_stock",
    )
    op.drop_column("mouvements_stock", "inventaire_id")

    op.drop_index(
        "ix_lignes_inventaire_emplacement_id",
        table_name="lignes_inventaire",
    )
    op.drop_constraint(
        "uq_lignes_inventaire_emplacement_article_lot",
        "lignes_inventaire",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_lignes_inventaire_article_lot",
        "lignes_inventaire",
        ["inventaire_id", "article_id", "lot_id"],
    )
    op.drop_column("lignes_inventaire", "emplacement_id")

    op.drop_index(
        "ix_inventaires_famille_id",
        table_name="inventaires",
    )
    op.drop_index(
        "ix_inventaires_type",
        table_name="inventaires",
    )
    op.alter_column(
        "inventaires",
        "emplacement_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("inventaires", "valide_par")
    op.drop_column("inventaires", "famille_id")
    op.drop_column("inventaires", "type")
