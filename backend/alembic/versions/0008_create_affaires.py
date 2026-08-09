"""Create business cases and link stock movements.

Revision ID: 0008
Revises: 0007
"""

from alembic import op
import sqlalchemy as sa

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS affaire_reference_seq START WITH 1"
    )

    op.create_table(
        "affaires",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'AFF-' || lpad(nextval('affaire_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column("code_externe", sa.String(length=80), nullable=True),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("client", sa.String(length=180), nullable=True),
        sa.Column("site", sa.String(length=180), nullable=True),
        sa.Column("zone_intervention", sa.String(length=180), nullable=True),
        sa.Column("charge_affaires", sa.String(length=150), nullable=True),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="OUVERTE"),
        sa.Column("date_debut", sa.Date(), nullable=True),
        sa.Column("date_fin_prevue", sa.Date(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
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
        sa.UniqueConstraint("reference", name="uq_affaires_reference"),
        sa.UniqueConstraint("code_externe", name="uq_affaires_code_externe"),
        sa.CheckConstraint(
            "date_fin_prevue IS NULL OR date_debut IS NULL OR date_fin_prevue >= date_debut",
            name="ck_affaires_dates_coherentes",
        ),
    )
    op.create_index("ix_affaires_statut", "affaires", ["statut"])
    op.create_index("ix_affaires_client", "affaires", ["client"])

    op.add_column(
        "mouvements_stock",
        sa.Column("affaire_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("zone_intervention", sa.String(length=180), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("charge_affaires", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("vehicule", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "mouvements_stock",
        sa.Column("sortie_libre", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_foreign_key(
        "fk_mouvements_stock_affaire_id",
        "mouvements_stock",
        "affaires",
        ["affaire_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_mouvements_stock_affaire_id",
        "mouvements_stock",
        ["affaire_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_stock_affaire_id",
        table_name="mouvements_stock",
    )
    op.drop_constraint(
        "fk_mouvements_stock_affaire_id",
        "mouvements_stock",
        type_="foreignkey",
    )
    op.drop_column("mouvements_stock", "sortie_libre")
    op.drop_column("mouvements_stock", "vehicule")
    op.drop_column("mouvements_stock", "charge_affaires")
    op.drop_column("mouvements_stock", "zone_intervention")
    op.drop_column("mouvements_stock", "affaire_id")

    op.drop_index("ix_affaires_client", table_name="affaires")
    op.drop_index("ix_affaires_statut", table_name="affaires")
    op.drop_table("affaires")
    op.execute("DROP SEQUENCE IF EXISTS affaire_reference_seq")
