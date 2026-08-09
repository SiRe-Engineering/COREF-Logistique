"""Add purchase receipt dates.
Revision ID: 0030
Revises: 0029
"""
from alembic import op
import sqlalchemy as sa
revision="0030"
down_revision="0029"
branch_labels=None
depends_on=None
def upgrade():
    op.add_column("commandes_achat",sa.Column("date_premiere_reception",sa.DateTime(timezone=True),nullable=True))
    op.add_column("commandes_achat",sa.Column("date_reception_finale",sa.DateTime(timezone=True),nullable=True))
    op.add_column("lignes_commandes_achat",sa.Column("date_premiere_reception",sa.DateTime(timezone=True),nullable=True))
    op.add_column("lignes_commandes_achat",sa.Column("date_derniere_reception",sa.DateTime(timezone=True),nullable=True))
def downgrade():
    op.drop_column("lignes_commandes_achat","date_derniere_reception")
    op.drop_column("lignes_commandes_achat","date_premiere_reception")
    op.drop_column("commandes_achat","date_reception_finale")
    op.drop_column("commandes_achat","date_premiere_reception")
