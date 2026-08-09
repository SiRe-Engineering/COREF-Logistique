"""Create concrete batches and batch-level stocks.

Revision ID: 0007
Revises: 0006
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS lot_beton_reference_seq START WITH 1"
    )

    op.create_table(
        "lots_beton",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference_interne",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'LOT-' || lpad(nextval('lot_beton_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("numero_lot_fournisseur", sa.String(length=120), nullable=False),
        sa.Column("date_fabrication", sa.Date(), nullable=False),
        sa.Column("date_peremption", sa.Date(), nullable=False),
        sa.Column("fournisseur", sa.String(length=180), nullable=True),
        sa.Column("certificat_reference", sa.String(length=255), nullable=True),
        sa.Column("fds_reference", sa.String(length=255), nullable=True),
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
            "reference_interne",
            name="uq_lots_beton_reference_interne",
        ),
        sa.UniqueConstraint(
            "article_id",
            "numero_lot_fournisseur",
            name="uq_lots_beton_article_numero_fournisseur",
        ),
        sa.CheckConstraint(
            "date_peremption >= date_fabrication",
            name="ck_lots_beton_dates_coherentes",
        ),
    )
    op.create_index("ix_lots_beton_article_id", "lots_beton", ["article_id"])
    op.create_index(
        "ix_lots_beton_date_peremption",
        "lots_beton",
        ["date_peremption"],
    )

    op.create_table(
        "stocks_lots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "lot_id",
            sa.Integer(),
            sa.ForeignKey("lots_beton.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "emplacement_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "quantite_physique",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "quantite_reservee",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "date_modification",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "quantite_physique >= 0",
            name="ck_stocks_lots_quantite_physique_positive",
        ),
        sa.CheckConstraint(
            "quantite_reservee >= 0",
            name="ck_stocks_lots_quantite_reservee_positive",
        ),
        sa.CheckConstraint(
            "quantite_reservee <= quantite_physique",
            name="ck_stocks_lots_reservee_inferieure_physique",
        ),
        sa.UniqueConstraint(
            "lot_id",
            "emplacement_id",
            name="uq_stocks_lots_lot_emplacement",
        ),
    )
    op.create_index("ix_stocks_lots_lot_id", "stocks_lots", ["lot_id"])
    op.create_index(
        "ix_stocks_lots_emplacement_id",
        "stocks_lots",
        ["emplacement_id"],
    )

    op.add_column(
        "mouvements_stock",
        sa.Column("lot_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_mouvements_stock_lot_id",
        "mouvements_stock",
        "lots_beton",
        ["lot_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_mouvements_stock_lot_id",
        "mouvements_stock",
        ["lot_id"],
    )

    # Reprise du stock béton existant dans un lot technique initial.
    connection = op.get_bind()

    articles_beton = connection.execute(
        sa.text(
            """
            SELECT a.id
            FROM articles a
            JOIN familles f ON f.id = a.famille_id
            WHERE f.code = 'BET'
              AND a.actif = true
            """
        )
    ).fetchall()

    for article_row in articles_beton:
        article_id = article_row.id

        lot_id = connection.execute(
            sa.text(
                """
                INSERT INTO lots_beton (
                    article_id,
                    numero_lot_fournisseur,
                    date_fabrication,
                    date_peremption,
                    fournisseur,
                    commentaire,
                    actif
                )
                VALUES (
                    :article_id,
                    'LOT-INITIAL',
                    CURRENT_DATE,
                    CURRENT_DATE + INTERVAL '10 years',
                    NULL,
                    'Lot technique créé automatiquement lors de la migration 0007.',
                    true
                )
                RETURNING id
                """
            ),
            {"article_id": article_id},
        ).scalar_one()

        connection.execute(
            sa.text(
                """
                INSERT INTO stocks_lots (
                    lot_id,
                    emplacement_id,
                    quantite_physique,
                    quantite_reservee
                )
                SELECT
                    :lot_id,
                    emplacement_id,
                    quantite_physique,
                    quantite_reservee
                FROM stocks
                WHERE article_id = :article_id
                  AND quantite_physique > 0
                """
            ),
            {
                "lot_id": lot_id,
                "article_id": article_id,
            },
        )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_stock_lot_id",
        table_name="mouvements_stock",
    )
    op.drop_constraint(
        "fk_mouvements_stock_lot_id",
        "mouvements_stock",
        type_="foreignkey",
    )
    op.drop_column("mouvements_stock", "lot_id")

    op.drop_index(
        "ix_stocks_lots_emplacement_id",
        table_name="stocks_lots",
    )
    op.drop_index("ix_stocks_lots_lot_id", table_name="stocks_lots")
    op.drop_table("stocks_lots")

    op.drop_index(
        "ix_lots_beton_date_peremption",
        table_name="lots_beton",
    )
    op.drop_index("ix_lots_beton_article_id", table_name="lots_beton")
    op.drop_table("lots_beton")
    op.execute("DROP SEQUENCE IF EXISTS lot_beton_reference_seq")
