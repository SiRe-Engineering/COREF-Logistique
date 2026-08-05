"""Create immutable stock movements.

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE SEQUENCE IF NOT EXISTS mouvement_reference_seq START WITH 1"
    )

    op.create_table(
        "mouvements_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "reference",
            sa.String(length=30),
            nullable=False,
            server_default=sa.text(
                "'MVT-' || lpad(nextval('mouvement_reference_seq')::text, 6, '0')"
            ),
        ),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "emplacement_source_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "emplacement_destination_id",
            sa.Integer(),
            sa.ForeignKey("emplacements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "quantite",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column("motif", sa.String(length=150), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("operateur", sa.String(length=120), nullable=True),
        sa.Column(
            "date_creation",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "quantite > 0",
            name="ck_mouvements_quantite_positive",
        ),
        sa.UniqueConstraint(
            "reference",
            name="uq_mouvements_reference",
        ),
    )

    op.create_index(
        "ix_mouvements_article_id",
        "mouvements_stock",
        ["article_id"],
    )
    op.create_index(
        "ix_mouvements_source_id",
        "mouvements_stock",
        ["emplacement_source_id"],
    )
    op.create_index(
        "ix_mouvements_destination_id",
        "mouvements_stock",
        ["emplacement_destination_id"],
    )
    op.create_index(
        "ix_mouvements_type",
        "mouvements_stock",
        ["type"],
    )
    op.create_index(
        "ix_mouvements_date_creation",
        "mouvements_stock",
        ["date_creation"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mouvements_date_creation",
        table_name="mouvements_stock",
    )
    op.drop_index("ix_mouvements_type", table_name="mouvements_stock")
    op.drop_index(
        "ix_mouvements_destination_id",
        table_name="mouvements_stock",
    )
    op.drop_index(
        "ix_mouvements_source_id",
        table_name="mouvements_stock",
    )
    op.drop_index(
        "ix_mouvements_article_id",
        table_name="mouvements_stock",
    )
    op.drop_table("mouvements_stock")
    op.execute("DROP SEQUENCE IF EXISTS mouvement_reference_seq")
