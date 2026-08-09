"""Create users and authentication sessions.

Revision ID: 0014
Revises: 0013
"""

from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "utilisateurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom_complet", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=180), nullable=False),
        sa.Column("mot_de_passe_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
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
        sa.UniqueConstraint("email", name="uq_utilisateurs_email"),
    )
    op.create_index("ix_utilisateurs_role", "utilisateurs", ["role"])
    op.create_index("ix_utilisateurs_actif", "utilisateurs", ["actif"])

    op.create_table(
        "sessions_utilisateur",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "utilisateur_id",
            sa.Integer(),
            sa.ForeignKey("utilisateurs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("jeton_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_expiration", sa.DateTime(timezone=True), nullable=False),
        sa.Column("date_revocation", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("jeton_hash", name="uq_sessions_jeton_hash"),
    )
    op.create_index(
        "ix_sessions_utilisateur_id",
        "sessions_utilisateur",
        ["utilisateur_id"],
    )
    op.create_index(
        "ix_sessions_date_expiration",
        "sessions_utilisateur",
        ["date_expiration"],
    )

    # Compte administrateur initial. Le mot de passe temporaire est Coref-2026!
    # Le hash est remplacé au premier démarrage par le script d'initialisation.
    op.execute(
        """
        INSERT INTO utilisateurs (
            nom_complet,
            email,
            mot_de_passe_hash,
            role,
            actif
        )
        VALUES (
            'Administrateur COREF',
            'admin@coref.fr',
            'INITIALISATION_REQUISE',
            'ADMINISTRATEUR',
            TRUE
        )
        """
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sessions_date_expiration",
        table_name="sessions_utilisateur",
    )
    op.drop_index(
        "ix_sessions_utilisateur_id",
        table_name="sessions_utilisateur",
    )
    op.drop_table("sessions_utilisateur")
    op.drop_index("ix_utilisateurs_actif", table_name="utilisateurs")
    op.drop_index("ix_utilisateurs_role", table_name="utilisateurs")
    op.drop_table("utilisateurs")
