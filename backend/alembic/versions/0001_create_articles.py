"""Create articles table.

Revision ID: 0001
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference", sa.String(length=80), nullable=False),
        sa.Column("designation", sa.String(length=255), nullable=False),
        sa.Column("famille", sa.String(length=120), nullable=True),
        sa.Column("sous_famille", sa.String(length=120), nullable=True),
        sa.Column("unite", sa.String(length=30), nullable=False, server_default="unité"),
        sa.Column(
            "stock_minimum",
            sa.Numeric(precision=12, scale=3),
            nullable=False,
            server_default="0",
        ),
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
    )
    op.create_index(
        "ix_articles_reference",
        "articles",
        ["reference"],
        unique=True,
    )
    op.create_index(
        "ix_articles_designation",
        "articles",
        ["designation"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_articles_designation", table_name="articles")
    op.drop_index("ix_articles_reference", table_name="articles")
    op.drop_table("articles")
