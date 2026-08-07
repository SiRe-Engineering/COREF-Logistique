"""Add persistent logistics alerts.

Revision ID: 0026
Revises: 0025
"""

from alembic import op
import sqlalchemy as sa


revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alertes_logistiques",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cle", sa.String(length=180), nullable=False),
        sa.Column("categorie", sa.String(length=40), nullable=False),
        sa.Column("niveau", sa.String(length=20), nullable=False),
        sa.Column("titre", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("lien", sa.String(length=255), nullable=True),
        sa.Column("source_type", sa.String(length=40), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column(
            "statut",
            sa.String(length=20),
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column(
            "date_premiere_detection",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "date_derniere_detection",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_resolution", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acquittee_par", sa.String(length=150), nullable=True),
        sa.Column("date_acquittement", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("cle", name="uq_alertes_logistiques_cle"),
    )
    op.create_index(
        "ix_alertes_logistiques_statut",
        "alertes_logistiques",
        ["statut"],
    )
    op.create_index(
        "ix_alertes_logistiques_categorie",
        "alertes_logistiques",
        ["categorie"],
    )
    op.create_index(
        "ix_alertes_logistiques_niveau",
        "alertes_logistiques",
        ["niveau"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_alertes_logistiques_niveau",
        table_name="alertes_logistiques",
    )
    op.drop_index(
        "ix_alertes_logistiques_categorie",
        table_name="alertes_logistiques",
    )
    op.drop_index(
        "ix_alertes_logistiques_statut",
        table_name="alertes_logistiques",
    )
    op.drop_table("alertes_logistiques")
