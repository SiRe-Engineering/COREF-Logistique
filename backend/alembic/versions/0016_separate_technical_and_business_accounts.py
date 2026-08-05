"""Separate SiRe Engineering technical account and COREF business accounts.

Revision ID: 0016
Revises: 0015
"""

from alembic import op
import sqlalchemy as sa

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "utilisateurs",
        sa.Column(
            "type_compte",
            sa.String(length=30),
            nullable=False,
            server_default="METIER",
        ),
    )
    op.add_column(
        "utilisateurs",
        sa.Column(
            "entreprise",
            sa.String(length=150),
            nullable=False,
            server_default="COREF",
        ),
    )
    op.add_column(
        "utilisateurs",
        sa.Column("prenom", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "utilisateurs",
        sa.Column("nom", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "utilisateurs",
        sa.Column("fonction", sa.String(length=150), nullable=True),
    )

    op.create_index(
        "ix_utilisateurs_type_compte",
        "utilisateurs",
        ["type_compte"],
    )
    op.create_index(
        "ix_utilisateurs_entreprise",
        "utilisateurs",
        ["entreprise"],
    )

    connection = op.get_bind()

    # Le compte créé précédemment devient le compte technique SiRe Engineering.
    connection.execute(
        sa.text(
            """
            UPDATE utilisateurs
            SET
                nom_complet = 'SiRe Engineering',
                email = 'contact@sire-engineering.fr',
                role = 'ADMINISTRATEUR_TECHNIQUE',
                type_compte = 'TECHNIQUE',
                entreprise = 'SiRe Engineering',
                prenom = NULL,
                nom = NULL,
                fonction = 'Éditeur et support de l’application'
            WHERE email IN (
                'admin@coref.local',
                'admin@coref.fr',
                'contact@sire-engineering.fr'
            )
            """
        )
    )

    # Premier administrateur métier COREF.
    connection.execute(
        sa.text(
            """
            INSERT INTO utilisateurs (
                nom_complet,
                email,
                mot_de_passe_hash,
                role,
                actif,
                type_compte,
                entreprise,
                prenom,
                nom,
                fonction
            )
            SELECT
                'Simon Goubet',
                'simon.goubet@coref.fr',
                'INITIALISATION_REQUISE',
                'ADMINISTRATEUR_COREF',
                TRUE,
                'METIER',
                'COREF',
                'Simon',
                'Goubet',
                'Directeur Général Adjoint'
            WHERE NOT EXISTS (
                SELECT 1
                FROM utilisateurs
                WHERE email = 'simon.goubet@coref.fr'
            )
            """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM utilisateurs
            WHERE email = 'simon.goubet@coref.fr'
              AND role = 'ADMINISTRATEUR_COREF'
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE utilisateurs
            SET
                nom_complet = 'Administrateur COREF',
                email = 'admin@coref.fr',
                role = 'ADMINISTRATEUR'
            WHERE email = 'contact@sire-engineering.fr'
              AND type_compte = 'TECHNIQUE'
            """
        )
    )

    op.drop_index(
        "ix_utilisateurs_entreprise",
        table_name="utilisateurs",
    )
    op.drop_index(
        "ix_utilisateurs_type_compte",
        table_name="utilisateurs",
    )
    op.drop_column("utilisateurs", "fonction")
    op.drop_column("utilisateurs", "nom")
    op.drop_column("utilisateurs", "prenom")
    op.drop_column("utilisateurs", "entreprise")
    op.drop_column("utilisateurs", "type_compte")
