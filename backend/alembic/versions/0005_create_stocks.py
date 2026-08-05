"""Create stock table and article stock thresholds.

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "articles",
        sa.Column(
            "stock_maximum",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
            server_default="0",
        ),
    )
    op.add_column(
        "articles",
        sa.Column(
            "seuil_alerte",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
            server_default="0",
        ),
    )

    op.create_table(
        "stocks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
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
            name="ck_stocks_quantite_physique_positive",
        ),
        sa.CheckConstraint(
            "quantite_reservee >= 0",
            name="ck_stocks_quantite_reservee_positive",
        ),
        sa.CheckConstraint(
            "quantite_reservee <= quantite_physique",
            name="ck_stocks_reservee_inferieure_physique",
        ),
        sa.UniqueConstraint(
            "article_id",
            "emplacement_id",
            name="uq_stocks_article_emplacement",
        ),
    )
    op.create_index("ix_stocks_article_id", "stocks", ["article_id"])
    op.create_index("ix_stocks_emplacement_id", "stocks", ["emplacement_id"])


def downgrade() -> None:
    op.drop_index("ix_stocks_emplacement_id", table_name="stocks")
    op.drop_index("ix_stocks_article_id", table_name="stocks")
    op.drop_table("stocks")
    op.drop_column("articles", "seuil_alerte")
    op.drop_column("articles", "stock_maximum")
