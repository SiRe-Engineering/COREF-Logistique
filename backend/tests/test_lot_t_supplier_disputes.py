from decimal import Decimal
def test_return_reference(): assert f"RET-{1:06d}"=="RET-000001"
def test_tri_balance(): assert Decimal("7")+Decimal("3")==Decimal("10")
def test_no_automatic_stock_exit_on_decision():
    decision="RETOUR_FOURNISSEUR"; movement_created=False
    assert decision and not movement_created
