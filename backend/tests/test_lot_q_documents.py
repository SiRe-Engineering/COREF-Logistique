import base64

def test_document_roundtrip_base64():
    contenu=b"%PDF-1.4 test"
    encode=base64.b64encode(contenu).decode()
    assert base64.b64decode(encode)==contenu

def test_beton_required_document_types():
    required={"CERTIFICAT","FDS"}
    present={"CERTIFICAT","FDS","BON_LIVRAISON"}
    assert required.issubset(present)
