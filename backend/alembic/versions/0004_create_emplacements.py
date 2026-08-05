"""Create hierarchical locations and seed COREF areas.

Revision ID: 0004
Revises: 0003
"""

from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

EMPLACEMENTS = [
    ("MEZ-ISO", "Mezzanine Isolants", "ZONE"),
    ("MAG-PRI", "Magasin Principal", "ZONE"),
    ("ZON-POC", "Zone Poche", "ZONE"),
    ("ZON-PRE", "Zone Préfa", "ZONE"),
    ("ZON-EMB", "Zone Emballage", "ZONE"),
    ("ZON-CHA", "Zone Chantier", "ZONE"),
    ("VEH", "Véhicules", "ZONE"),
    ("CON-FCR", "Container FCR", "ZONE"),
    ("LOC-RES", "Local Résine", "ZONE"),
    ("RAC-MOU", "Racks Moules", "ZONE"),
]


def upgrade() -> None:
    op.create_table(
        "emplacements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("nom", sa.String(length=150), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("allee", sa.String(length=5), nullable=True),
        sa.Column("rack", sa.String(length=10), nullable=True),
        sa.Column("etage", sa.Integer(), nullable=True),
        sa.Column("case", sa.String(length=5), nullable=True),
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
        sa.UniqueConstraint("code", name="uq_emplacements_code"),
    )
    op.create_index("ix_emplacements_parent_id", "emplacements", ["parent_id"])
    op.create_index("ix_emplacements_type", "emplacements", ["type"])

    table = sa.table(
        "emplacements",
        sa.column("code", sa.String()),
        sa.column("nom", sa.String()),
        sa.column("type", sa.String()),
        sa.column("actif", sa.Boolean()),
    )

    op.bulk_insert(
        table,
        [
            {"code": code, "nom": nom, "type": type_, "actif": True}
            for code, nom, type_ in EMPLACEMENTS
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_emplacements_type", table_name="emplacements")
    op.drop_index("ix_emplacements_parent_id", table_name="emplacements")
    op.drop_table("emplacements")
