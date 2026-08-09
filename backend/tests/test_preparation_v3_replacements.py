from decimal import Decimal

from app.models.preparation import LignePreparation


def test_ligne_expose_proposition_remplacement():
    ligne = LignePreparation(
        preparation_id=1,
        article_id=10,
        quantite_demandee=Decimal("5"),
        quantite_preparee=Decimal("0"),
        quantite_manquante=Decimal("5"),
        statut="INDISPONIBLE",
    )

    ligne.article_remplacement_id = 20
    ligne.lot_remplacement_id = 30
    ligne.emplacement_remplacement_id = 40
    ligne.quantite_remplacement = Decimal("5")
    ligne.commentaire_remplacement = "Article alternatif proposé"
    ligne.propose_par = "Préparateur"
    ligne.statut = "REMPLACEMENT_PROPOSE"

    assert ligne.article_remplacement_id == 20
    assert ligne.lot_remplacement_id == 30
    assert ligne.emplacement_remplacement_id == 40
    assert ligne.quantite_remplacement == Decimal("5")
    assert ligne.commentaire_remplacement == "Article alternatif proposé"
    assert ligne.statut == "REMPLACEMENT_PROPOSE"


def test_ligne_expose_decision_remplacement():
    ligne = LignePreparation(
        preparation_id=1,
        article_id=10,
        quantite_demandee=Decimal("5"),
        quantite_preparee=Decimal("0"),
        quantite_manquante=Decimal("5"),
        statut="REMPLACEMENT_PROPOSE",
        article_remplacement_id=20,
        quantite_remplacement=Decimal("5"),
        commentaire_remplacement="Alternative proposée",
    )

    ligne.decision_remplacement = "ACCEPTE"
    ligne.decision_par = "Demandeur"
    ligne.commentaire_decision = "Validé"
    ligne.statut = "REMPLACEMENT_ACCEPTE"

    assert ligne.decision_remplacement == "ACCEPTE"
    assert ligne.decision_par == "Demandeur"
    assert ligne.commentaire_decision == "Validé"
    assert ligne.statut == "REMPLACEMENT_ACCEPTE"
