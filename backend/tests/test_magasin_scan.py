from app.api.magasin import normaliser_scan


def test_normaliser_scan() -> None:
    assert normaliser_scan("  ART-000123\r\n") == "ART-000123"


def test_normaliser_lot() -> None:
    assert normaliser_scan("LOT-000004") == "LOT-000004"
