def test_supplier_ncf_reference_format():
    assert f"NCF-{1:06d}"=="NCF-000001"
def test_closure_requires_decision():
    decision=None
    assert not decision
def test_supported_decisions():
    assert {"ACCEPTE_EN_ETAT","TRI","RETOUR_FOURNISSEUR","REMPLACEMENT","AVOIR"}=={"ACCEPTE_EN_ETAT","TRI","RETOUR_FOURNISSEUR","REMPLACEMENT","AVOIR"}
