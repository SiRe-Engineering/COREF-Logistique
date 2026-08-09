"""Equipment documents. Revision ID: 0037, Revises: 0036."""
from alembic import op
import sqlalchemy as sa
revision="0037";down_revision="0036";branch_labels=None;depends_on=None
def upgrade():
    op.create_table("documents_materiel",
      sa.Column("id",sa.Integer(),primary_key=True),
      sa.Column("materiel_id",sa.Integer(),sa.ForeignKey("materiels.id",ondelete="CASCADE"),nullable=False),
      sa.Column("type_document",sa.String(50),nullable=False),
      sa.Column("nom_fichier",sa.String(255),nullable=False),
      sa.Column("type_mime",sa.String(100),nullable=False),
      sa.Column("taille_octets",sa.Integer(),nullable=False),
      sa.Column("contenu",sa.LargeBinary(),nullable=False),
      sa.Column("reference_document",sa.String(150),nullable=True),
      sa.Column("date_document",sa.Date(),nullable=True),
      sa.Column("date_expiration",sa.Date(),nullable=True),
      sa.Column("organisme",sa.String(180),nullable=True),
      sa.Column("commentaire",sa.Text(),nullable=True),
      sa.Column("date_depot",sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
      sa.Column("depose_par",sa.String(150),nullable=True))
    op.create_index("ix_documents_materiel_materiel","documents_materiel",["materiel_id"])
    op.create_index("ix_documents_materiel_expiration","documents_materiel",["date_expiration"])
def downgrade():
    op.drop_index("ix_documents_materiel_expiration",table_name="documents_materiel")
    op.drop_index("ix_documents_materiel_materiel",table_name="documents_materiel")
    op.drop_table("documents_materiel")
