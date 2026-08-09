"""Reconcile preparation reservations.

Revision ID: 0013
Revises: 0012
"""

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    maintenant = datetime.now(timezone.utc)

    # Les préparations actives deviennent l'unique source de vérité.
    connection.execute(
        sa.text(
            """
            UPDATE reservations_stock
            SET statut = 'LIBEREE',
                date_liberation = :maintenant
            WHERE statut = 'ACTIVE'
            """
        ),
        {"maintenant": maintenant},
    )

    connection.execute(
        sa.text("UPDATE stocks SET quantite_reservee = 0")
    )
    connection.execute(
        sa.text("UPDATE stocks_lots SET quantite_reservee = 0")
    )

    lignes = connection.execute(
        sa.text(
            """
            SELECT
                lp.id AS ligne_id,
                lp.article_id,
                lp.lot_id,
                lp.emplacement_source_id,
                lp.quantite_demandee,
                p.id AS preparation_id,
                p.reference AS preparation_reference,
                p.nom AS preparation_nom,
                p.demandeur,
                a.reference AS affaire_reference,
                a.code_externe AS affaire_code
            FROM lignes_preparation lp
            JOIN preparations p ON p.id = lp.preparation_id
            JOIN affaires a ON a.id = p.affaire_id
            WHERE p.statut IN ('VALIDEE', 'EN_PREPARATION', 'PRETE')
              AND lp.emplacement_source_id IS NOT NULL
              AND lp.quantite_demandee > 0
            ORDER BY lp.id
            """
        )
    ).mappings().all()

    for ligne in lignes:
        reserve_pour = (
            f"{ligne['preparation_reference']} — "
            f"{ligne['affaire_code'] or ligne['affaire_reference']}"
        )

        connection.execute(
            sa.text(
                """
                INSERT INTO reservations_stock (
                    article_id,
                    lot_id,
                    emplacement_id,
                    preparation_id,
                    ligne_preparation_id,
                    quantite,
                    reserve_pour,
                    reserve_par,
                    motif,
                    statut,
                    date_creation
                )
                VALUES (
                    :article_id,
                    :lot_id,
                    :emplacement_id,
                    :preparation_id,
                    :ligne_id,
                    :quantite,
                    :reserve_pour,
                    :reserve_par,
                    :motif,
                    'ACTIVE',
                    :maintenant
                )
                ON CONFLICT (ligne_preparation_id)
                DO UPDATE SET
                    article_id = EXCLUDED.article_id,
                    lot_id = EXCLUDED.lot_id,
                    emplacement_id = EXCLUDED.emplacement_id,
                    preparation_id = EXCLUDED.preparation_id,
                    quantite = EXCLUDED.quantite,
                    reserve_pour = EXCLUDED.reserve_pour,
                    reserve_par = EXCLUDED.reserve_par,
                    motif = EXCLUDED.motif,
                    statut = 'ACTIVE',
                    date_liberation = NULL
                """
            ),
            {
                "article_id": ligne["article_id"],
                "lot_id": ligne["lot_id"],
                "emplacement_id": ligne["emplacement_source_id"],
                "preparation_id": ligne["preparation_id"],
                "ligne_id": ligne["ligne_id"],
                "quantite": ligne["quantite_demandee"],
                "reserve_pour": reserve_pour,
                "reserve_par": ligne["demandeur"],
                "motif": ligne["preparation_nom"],
                "maintenant": maintenant,
            },
        )

        connection.execute(
            sa.text(
                """
                UPDATE stocks
                SET quantite_reservee =
                    quantite_reservee + :quantite
                WHERE article_id = :article_id
                  AND emplacement_id = :emplacement_id
                """
            ),
            {
                "quantite": ligne["quantite_demandee"],
                "article_id": ligne["article_id"],
                "emplacement_id": ligne["emplacement_source_id"],
            },
        )

        if ligne["lot_id"] is not None:
            connection.execute(
                sa.text(
                    """
                    UPDATE stocks_lots
                    SET quantite_reservee =
                        quantite_reservee + :quantite
                    WHERE lot_id = :lot_id
                      AND emplacement_id = :emplacement_id
                    """
                ),
                {
                    "quantite": ligne["quantite_demandee"],
                    "lot_id": ligne["lot_id"],
                    "emplacement_id": ligne["emplacement_source_id"],
                },
            )


def downgrade() -> None:
    # La réconciliation n'ajoute aucune structure.
    # Un retour arrière automatique risquerait de restaurer des incohérences.
    pass
