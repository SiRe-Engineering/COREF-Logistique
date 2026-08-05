"""Create families and subfamilies tables and seed COREF data.

Revision ID: 0002
Revises: 0001
"""

from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

FAMILLES = [
    ("ISO", "Isolants"),
    ("BET", "Béton"),
    ("BRI", "Briques"),
    ("ANC", "Ancrages"),
    ("CON", "Consommable"),
    ("EPI", "EPI"),
    ("PRE", "Pièces Préfabriquées"),
    ("MAT", "Matériel"),
    ("MOU", "Moules"),
]

SOUS_FAMILLES = {
    "ISO": [
        ("MIC", "Panneaux Microporeux"),
        ("BOA", "Panneaux Board"),
        ("PAP", "Papers"),
        ("NAP", "Nappes"),
        ("MOD", "Modules"),
        ("FVR", "Fibre en vrac"),
        ("SIL", "Panneaux Silicate de Calcium"),
        ("TRE", "Tresses"),
        ("FPI", "Panneaux FPI"),
    ],
    "BET": [
        ("DEN", "Dense"),
        ("ISO", "Isolant"),
        ("GUN", "Gunitable"),
        ("AUT", "Autocoulable"),
    ],
    "BRI": [("DEN", "Dense"), ("ISO", "Isolante")],
    "ANC": [("BET", "Béton"), ("FIB", "Fibre")],
    "CON": [
        ("EMB", "Consommables d’Emballage"),
        ("QUI", "Quincaillerie"),
        ("LEV", "Consommables de Levage"),
        ("BOI", "Bois de coffrage"),
        ("CHI", "Produits chimiques"),
        ("FUM", "Consommables de Fumisterie"),
        ("ELE", "Consommables Électriques"),
    ],
    "EPI": [
        ("CAS", "Casques / Casquettes"),
        ("GAN", "Gants"),
        ("CHA", "Chaussures"),
        ("VET", "Vêtements"),
        ("VUE", "Protections de la vue"),
        ("AUD", "Protections auditives"),
        ("RES", "Protections respiratoires"),
    ],
    "MAT": [
        ("MAL", "Malaxeur"),
        ("SCI", "Scie à Briques"),
        ("ELP", "Électroportatif"),
        ("AIR", "Air comprimé"),
    ],
}


def upgrade() -> None:
    op.create_table(
        "familles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("nom", sa.String(length=120), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modification", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_familles_code"),
        sa.UniqueConstraint("nom", name="uq_familles_nom"),
    )

    op.create_table(
        "sous_familles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("famille_id", sa.Integer(), sa.ForeignKey("familles.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("nom", sa.String(length=120), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("date_creation", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("date_modification", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("famille_id", "code", name="uq_sous_familles_famille_code"),
        sa.UniqueConstraint("famille_id", "nom", name="uq_sous_familles_famille_nom"),
    )
    op.create_index("ix_sous_familles_famille_id", "sous_familles", ["famille_id"])

    connection = op.get_bind()
    familles_table = sa.table(
        "familles",
        sa.column("id", sa.Integer()),
        sa.column("code", sa.String()),
        sa.column("nom", sa.String()),
        sa.column("actif", sa.Boolean()),
    )
    sous_familles_table = sa.table(
        "sous_familles",
        sa.column("famille_id", sa.Integer()),
        sa.column("code", sa.String()),
        sa.column("nom", sa.String()),
        sa.column("actif", sa.Boolean()),
    )

    connection.execute(
        familles_table.insert(),
        [{"code": code, "nom": nom, "actif": True} for code, nom in FAMILLES],
    )

    famille_ids = {
        row.code: row.id
        for row in connection.execute(sa.select(familles_table.c.id, familles_table.c.code))
    }

    rows = []
    for famille_code, valeurs in SOUS_FAMILLES.items():
        for code, nom in valeurs:
            rows.append(
                {
                    "famille_id": famille_ids[famille_code],
                    "code": code,
                    "nom": nom,
                    "actif": True,
                }
            )
    connection.execute(sous_familles_table.insert(), rows)


def downgrade() -> None:
    op.drop_index("ix_sous_familles_famille_id", table_name="sous_familles")
    op.drop_table("sous_familles")
    op.drop_table("familles")
