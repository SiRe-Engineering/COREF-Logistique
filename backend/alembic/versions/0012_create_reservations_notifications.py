"""Create stock reservations and user notifications.

Revision ID: 0012
Revises: 0011
"""

from alembic import op
import sqlalchemy as sa

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS reservation_reference_seq START WITH 1"
    )

    op.create_table(
        "reservations_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'RES-' || lpad(nextval('reservation_reference_seq')::text, 6, '0')"
            ),
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
            "emplacement_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "preparation_id",
            sa.Integer(),
            sa.ForeignKey("preparations.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "ligne_preparation_id",
            sa.Integer(),
            sa.ForeignKey("lignes_preparation.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "quantite",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column("reserve_pour", sa.String(length=200), nullable=False),
        sa.Column("reserve_par", sa.String(length=120), nullable=True),
        sa.Column("motif", sa.String(length=255), nullable=True),
        sa.Column("statut", sa.String(length=30), nullable=False, server_default="ACTIVE"),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_liberation", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("reference", name="uq_reservations_reference"),
        sa.UniqueConstraint(
            "ligne_preparation_id",
            name="uq_reservations_ligne_preparation",
        ),
        sa.CheckConstraint(
            "quantite > 0",
            name="ck_reservations_quantite_positive",
        ),
    )
    op.create_index(
        "ix_reservations_article_emplacement",
        "reservations_stock",
        ["article_id", "emplacement_id"],
    )
    op.create_index(
        "ix_reservations_preparation_id",
        "reservations_stock",
        ["preparation_id"],
    )
    op.create_index(
        "ix_reservations_statut",
        "reservations_stock",
        ["statut"],
    )

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("destinataire", sa.String(length=120), nullable=False),
        sa.Column("titre", sa.String(length=180), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False, server_default="INFORMATION"),
        sa.Column("lien", sa.String(length=255), nullable=True),
        sa.Column("lue", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("date_lecture", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_notifications_destinataire_lue",
        "notifications",
        ["destinataire", "lue"],
    )

    # Reprise des réservations historiques saisies manuellement.
    connection = op.get_bind()
    stocks_reserves = connection.execute(
        sa.text(
            """
            SELECT article_id, emplacement_id, quantite_reservee
            FROM stocks
            WHERE quantite_reservee > 0
            """
        )
    ).fetchall()

    for stock in stocks_reserves:
        connection.execute(
            sa.text(
                """
                INSERT INTO reservations_stock (
                    article_id,
                    emplacement_id,
                    quantite,
                    reserve_pour,
                    reserve_par,
                    motif,
                    statut
                )
                VALUES (
                    :article_id,
                    :emplacement_id,
                    :quantite,
                    'Reprise historique',
                    'Migration 0012',
                    'Quantité réservée existante avant la gestion détaillée',
                    'ACTIVE'
                )
                """
            ),
            {
                "article_id": stock.article_id,
                "emplacement_id": stock.emplacement_id,
                "quantite": stock.quantite_reservee,
            },
        )


def downgrade() -> None:
    op.drop_index(
        "ix_notifications_destinataire_lue",
        table_name="notifications",
    )
    op.drop_table("notifications")

    op.drop_index("ix_reservations_statut", table_name="reservations_stock")
    op.drop_index(
        "ix_reservations_preparation_id",
        table_name="reservations_stock",
    )
    op.drop_index(
        "ix_reservations_article_emplacement",
        table_name="reservations_stock",
    )
    op.drop_table("reservations_stock")
    op.execute("DROP SEQUENCE IF EXISTS reservation_reference_seq")
