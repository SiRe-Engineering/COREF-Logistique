"""Add replenishment needs.

Revision ID: 0027
Revises: 0026
"""

from alembic import op
import sqlalchemy as sa


revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS besoin_reappro_reference_seq START 1"
    )
    op.create_table(
        "besoins_reapprovisionnement",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'REA-' || lpad("
                "nextval('besoin_reappro_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("quantite_suggeree", sa.Numeric(14, 3), nullable=False),
        sa.Column("quantite_demandee", sa.Numeric(14, 3), nullable=False),
        sa.Column(
            "quantite_commandee",
            sa.Numeric(14, 3),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "quantite_recue",
            sa.Numeric(14, 3),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "prix_unitaire_prevu",
            sa.Numeric(14, 4),
            nullable=True,
        ),
        sa.Column("fournisseur", sa.String(length=180), nullable=True),
        sa.Column(
            "reference_commande",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "statut",
            sa.String(length=30),
            nullable=False,
            server_default="A_TRAITER",
        ),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("cree_par", sa.String(length=150), nullable=True),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "date_modification",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_validation", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_commande", sa.DateTime(timezone=True), nullable=True),
        sa.Column("date_cloture", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("reference"),
    )
    op.create_index(
        "ix_besoins_reappro_article",
        "besoins_reapprovisionnement",
        ["article_id"],
    )
    op.create_index(
        "ix_besoins_reappro_statut",
        "besoins_reapprovisionnement",
        ["statut"],
    )

    op.add_column(
        "mouvements_stock",
        sa.Column(
            "besoin_reapprovisionnement_id",
            sa.Integer(),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_mouvements_besoin_reappro",
        "mouvements_stock",
        "besoins_reapprovisionnement",
        ["besoin_reapprovisionnement_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_mouvements_besoin_reappro",
        "mouvements_stock",
        ["besoin_reapprovisionnement_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_besoin_reappro",
        table_name="mouvements_stock",
    )
    op.drop_constraint(
        "fk_mouvements_besoin_reappro",
        "mouvements_stock",
        type_="foreignkey",
    )
    op.drop_column(
        "mouvements_stock",
        "besoin_reapprovisionnement_id",
    )
    op.drop_index(
        "ix_besoins_reappro_statut",
        table_name="besoins_reapprovisionnement",
    )
    op.drop_index(
        "ix_besoins_reappro_article",
        table_name="besoins_reapprovisionnement",
    )
    op.drop_table("besoins_reapprovisionnement")
    op.execute("DROP SEQUENCE IF EXISTS besoin_reappro_reference_seq")
