"""Link articles to families and add automatic references.

Revision ID: 0003
Revises: 0002
"""

from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SEQUENCE IF NOT EXISTS article_reference_seq START WITH 1")

    op.add_column(
        "articles",
        sa.Column("famille_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "articles",
        sa.Column("sous_famille_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_articles_famille_id",
        "articles",
        "familles",
        ["famille_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_articles_sous_famille_id",
        "articles",
        "sous_familles",
        ["sous_famille_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_articles_famille_id", "articles", ["famille_id"])
    op.create_index("ix_articles_sous_famille_id", "articles", ["sous_famille_id"])

    op.alter_column(
        "articles",
        "reference",
        existing_type=sa.String(length=80),
        server_default=sa.text(
            "'ART-' || lpad(nextval('article_reference_seq')::text, 6, '0')"
        ),
    )


def downgrade() -> None:
    op.alter_column(
        "articles",
        "reference",
        existing_type=sa.String(length=80),
        server_default=None,
    )
    op.drop_index("ix_articles_sous_famille_id", table_name="articles")
    op.drop_index("ix_articles_famille_id", table_name="articles")
    op.drop_constraint(
        "fk_articles_sous_famille_id",
        "articles",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_articles_famille_id",
        "articles",
        type_="foreignkey",
    )
    op.drop_column("articles", "sous_famille_id")
    op.drop_column("articles", "famille_id")
    op.execute("DROP SEQUENCE IF EXISTS article_reference_seq")
