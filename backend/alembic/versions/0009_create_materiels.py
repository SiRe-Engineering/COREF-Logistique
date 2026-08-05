"""Create equipment register.

Revision ID: 0009
Revises: 0008
"""

from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS materiel_reference_seq START WITH 1"
    )

    op.create_table(
        "materiels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "numero_inventaire",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'MAT-' || lpad(nextval('materiel_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column("designation", sa.String(length=200), nullable=False),
        sa.Column("categorie", sa.String(length=80), nullable=False),
        sa.Column("marque", sa.String(length=120), nullable=True),
        sa.Column("modele", sa.String(length=120), nullable=True),
        sa.Column("numero_serie", sa.String(length=150), nullable=True),
        sa.Column("etat", sa.String(length=30), nullable=False, server_default="DISPONIBLE"),
        sa.Column(
            "emplacement_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "affaire_id",
            sa.Integer(),
            sa.ForeignKey("affaires.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("date_achat", sa.Date(), nullable=True),
        sa.Column("valeur_achat", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("date_dernier_controle", sa.Date(), nullable=True),
        sa.Column("date_prochain_controle", sa.Date(), nullable=True),
        sa.Column("type_controle", sa.String(length=120), nullable=True),
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
        sa.UniqueConstraint(
            "numero_inventaire",
            name="uq_materiels_numero_inventaire",
        ),
        sa.UniqueConstraint(
            "numero_serie",
            name="uq_materiels_numero_serie",
        ),
        sa.CheckConstraint(
            "date_prochain_controle IS NULL OR date_dernier_controle IS NULL OR date_prochain_controle >= date_dernier_controle",
            name="ck_materiels_dates_controle",
        ),
        sa.CheckConstraint(
            "valeur_achat IS NULL OR valeur_achat >= 0",
            name="ck_materiels_valeur_positive",
        ),
    )

    op.create_index("ix_materiels_categorie", "materiels", ["categorie"])
    op.create_index("ix_materiels_etat", "materiels", ["etat"])
    op.create_index("ix_materiels_emplacement_id", "materiels", ["emplacement_id"])
    op.create_index("ix_materiels_affaire_id", "materiels", ["affaire_id"])
    op.create_index(
        "ix_materiels_date_prochain_controle",
        "materiels",
        ["date_prochain_controle"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_materiels_date_prochain_controle",
        table_name="materiels",
    )
    op.drop_index("ix_materiels_affaire_id", table_name="materiels")
    op.drop_index("ix_materiels_emplacement_id", table_name="materiels")
    op.drop_index("ix_materiels_etat", table_name="materiels")
    op.drop_index("ix_materiels_categorie", table_name="materiels")
    op.drop_table("materiels")
    op.execute("DROP SEQUENCE IF EXISTS materiel_reference_seq")
