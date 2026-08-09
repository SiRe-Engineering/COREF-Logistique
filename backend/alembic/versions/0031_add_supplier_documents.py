"""Add supplier quality documents.

Revision ID: 0031
Revises: 0030
"""
from alembic import op
import sqlalchemy as sa

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents_fournisseurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type_document", sa.String(40), nullable=False),
        sa.Column("nom_fichier", sa.String(255), nullable=False),
        sa.Column("type_mime", sa.String(120), nullable=False),
        sa.Column("taille_octets", sa.Integer(), nullable=False),
        sa.Column("contenu", sa.LargeBinary(), nullable=False),
        sa.Column(
            "lot_beton_id",
            sa.Integer(),
            sa.ForeignKey("lots_beton.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column(
            "fournisseur_id",
            sa.Integer(),
            sa.ForeignKey("fournisseurs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "commande_achat_id",
            sa.Integer(),
            sa.ForeignKey("commandes_achat.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "article_id",
            sa.Integer(),
            sa.ForeignKey("articles.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("reference_document", sa.String(255), nullable=True),
        sa.Column("date_document", sa.Date(), nullable=True),
        sa.Column("date_expiration", sa.Date(), nullable=True),
        sa.Column("commentaire", sa.Text(), nullable=True),
        sa.Column("depose_par", sa.String(150), nullable=True),
        sa.Column(
            "date_depot",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index(
        "ix_documents_fournisseurs_lot",
        "documents_fournisseurs",
        ["lot_beton_id"],
    )
    op.create_index(
        "ix_documents_fournisseurs_fournisseur",
        "documents_fournisseurs",
        ["fournisseur_id"],
    )
    op.create_index(
        "ix_documents_fournisseurs_commande",
        "documents_fournisseurs",
        ["commande_achat_id"],
    )
    op.create_index(
        "ix_documents_fournisseurs_article",
        "documents_fournisseurs",
        ["article_id"],
    )
    op.create_index(
        "ix_documents_fournisseurs_type",
        "documents_fournisseurs",
        ["type_document"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_documents_fournisseurs_type",
        table_name="documents_fournisseurs",
    )
    op.drop_index(
        "ix_documents_fournisseurs_article",
        table_name="documents_fournisseurs",
    )
    op.drop_index(
        "ix_documents_fournisseurs_commande",
        table_name="documents_fournisseurs",
    )
    op.drop_index(
        "ix_documents_fournisseurs_fournisseur",
        table_name="documents_fournisseurs",
    )
    op.drop_index(
        "ix_documents_fournisseurs_lot",
        table_name="documents_fournisseurs",
    )
    op.drop_table("documents_fournisseurs")
