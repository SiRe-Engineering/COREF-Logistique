from datetime import date


def nom_inventaire(
    jour: date,
    type_inventaire: str,
    libelle: str | None = None,
) -> str:
    base = jour.isoformat()

    if type_inventaire == "EMPLACEMENT":
        return f"{base} - Emplacement - {libelle}"
    if type_inventaire == "FAMILLE":
        return f"{base} - Famille - {libelle}"
    return f"{base} - Général"


def test_nom_emplacement() -> None:
    assert nom_inventaire(
        date(2026, 8, 6),
        "EMPLACEMENT",
        "Magasin Principal",
    ) == "2026-08-06 - Emplacement - Magasin Principal"


def test_nom_famille() -> None:
    assert nom_inventaire(
        date(2026, 8, 6),
        "FAMILLE",
        "Béton",
    ) == "2026-08-06 - Famille - Béton"


def test_nom_general() -> None:
    assert nom_inventaire(
        date(2026, 8, 6),
        "GENERAL",
    ) == "2026-08-06 - Général"
