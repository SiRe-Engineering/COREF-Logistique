"""Create inventory campaigns and lines.

Revision ID: 0010
Revises: 0009
"""

from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS inventaire_reference_seq START WITH 1"
    )

    op.create_table(
        "inventaires",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'INV-' || lpad(nextval('inventaire_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column("nom", sa.String(length=180), nullable=False),
        sa.Column(
            "emplacement_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="BROUILLON"),
        sa.Column("operateur", sa.String(length=120), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_validation", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("reference", name="uq_inventaires_reference"),
    )
    op.create_index("ix_inventaires_emplacement_id", "inventaires", ["emplacement_id"])
    op.create_index("ix_inventaires_statut", "inventaires", ["statut"])

    op.create_table(
        "lignes_inventaire",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "inventaire_id",
            sa.Integer(),
            sa.ForeignKey("inventaires.id", ondelete="CASCADE"),
            nullable=False,
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
            "quantite_theorique",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "quantite_comptee",
            sa.Numeric(precision=14, scale=3),
            nullable=True,
        ),
        sa.Column("commentaire", sa.String(length=255), nullable=True),
        sa.UniqueConstraint(
            "inventaire_id",
            "article_id",
            "lot_id",
            name="uq_lignes_inventaire_article_lot",
        ),
    )
    op.create_index(
        "ix_lignes_inventaire_inventaire_id",
        "lignes_inventaire",
        ["inventaire_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lignes_inventaire_inventaire_id",
        table_name="lignes_inventaire",
    )
    op.drop_table("lignes_inventaire")
    op.drop_index("ix_inventaires_statut", table_name="inventaires")
    op.drop_index("ix_inventaires_emplacement_id", table_name="inventaires")
    op.drop_table("inventaires")
    op.execute("DROP SEQUENCE IF EXISTS inventaire_reference_seq")
