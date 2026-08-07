from app.services.qrcode import matrix, svg


def test_qr_reference_article() -> None:
    modules = matrix("ART-000001")
    assert len(modules) == 21
    assert all(len(row) == 21 for row in modules)
    assert sum(sum(row) for row in modules) > 100


def test_qr_svg() -> None:
    contenu = svg("LOT-000001")
    assert contenu.startswith("<svg")
    assert "<path" in contenu
    assert "shape-rendering" in contenu
