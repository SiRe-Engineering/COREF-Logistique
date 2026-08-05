from app.schemas.famille import FamilleCreate, SousFamilleCreate


def test_normalisation_famille() -> None:
    famille = FamilleCreate(code=" mou ", nom=" Moules ")
    assert famille.code == "MOU"
    assert famille.nom == "Moules"


def test_normalisation_sous_famille() -> None:
    sous_famille = SousFamilleCreate(
        famille_id=1,
        code=" mal ",
        nom=" Malaxeur ",
    )
    assert sous_famille.code == "MAL"
    assert sous_famille.nom == "Malaxeur"
