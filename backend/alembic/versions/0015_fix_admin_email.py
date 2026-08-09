"""Replace invalid local administrator email.

Revision ID: 0015
Revises: 0014
"""

from alembic import op
import sqlalchemy as sa

revision = "0015"
down_revision = "0014"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE utilisateurs
            SET email = 'admin@coref.fr'
            WHERE email = 'admin@coref.local'
            """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            UPDATE utilisateurs
            SET email = 'admin@coref.local'
            WHERE email = 'admin@coref.fr'
            """
        )
    )
