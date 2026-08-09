"""Create job preparation orders.

Revision ID: 0011
Revises: 0010
"""

from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS preparation_reference_seq START WITH 1"
    )

    op.create_table(
        "preparations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'PREP-' || lpad(nextval('preparation_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column(
            "affaire_id",
            sa.Integer(),
            sa.ForeignKey("affaires.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="BROUILLON"),
        sa.Column("date_besoin", sa.Date(), nullable=True),
        sa.Column("demandeur", sa.String(length=120), nullable=True),
        sa.Column("preparateur", sa.String(length=120), nullable=True),
        sa.Column("vehicule", sa.String(length=120), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_validation", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_expedition", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("reference", name="uq_preparations_reference"),
    )
    op.create_index("ix_preparations_affaire_id", "preparations", ["affaire_id"])
    op.create_index("ix_preparations_statut", "preparations", ["statut"])

    op.create_table(
        "lignes_preparation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "preparation_id",
            sa.Integer(),
            sa.ForeignKey("preparations.id", ondelete="CASCADE"),
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
            "emplacement_source_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "quantite_demandee",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "quantite_preparee",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0",
        ),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="A_PREPARER"),
        sa.Column("commentaire", sa.String(length=255), nullable=True),
        sa.CheckConstraint(
            "quantite_demandee > 0",
            name="ck_lignes_preparation_quantite_demandee_positive",
        ),
        sa.CheckConstraint(
            "quantite_preparee >= 0",
            name="ck_lignes_preparation_quantite_preparee_positive",
        ),
    )
    op.create_index(
        "ix_lignes_preparation_preparation_id",
        "lignes_preparation",
        ["preparation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lignes_preparation_preparation_id",
        table_name="lignes_preparation",
    )
    op.drop_table("lignes_preparation")
    op.drop_index("ix_preparations_statut", table_name="preparations")
    op.drop_index("ix_preparations_affaire_id", table_name="preparations")
    op.drop_table("preparations")
    op.execute("DROP SEQUENCE IF EXISTS preparation_reference_seq")
