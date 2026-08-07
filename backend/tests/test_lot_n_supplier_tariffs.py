from decimal import Decimal

from app.services.reapprovisionnement import quantite_suggeree


def test_reappro_at_alert_level_remains_safe() -> None:
    assert quantite_suggeree(
        disponible=Decimal("10"),
        minimum=Decimal("10"),
        maximum=Decimal("0"),
        seuil_alerte=Decimal("10"),
    ) == Decimal("10")


def test_reappro_targets_maximum_when_defined() -> None:
    assert quantite_suggeree(
        disponible=Decimal("10"),
        minimum=Decimal("10"),
        maximum=Decimal("30"),
        seuil_alerte=Decimal("10"),
    ) == Decimal("20")
