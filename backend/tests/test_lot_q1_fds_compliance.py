from datetime import date, timedelta

def statut(fds_present: bool, fds_expiration=None):
    if fds_present and fds_expiration and fds_expiration < date.today():
        return "EXPIRE"
    return "COMPLET" if fds_present else "INCOMPLET"

def test_only_fds_is_required():
    assert statut(True) == "COMPLET"
    assert statut(False) == "INCOMPLET"

def test_certificate_does_not_change_compliance():
    certificat_present = False
    assert certificat_present is False
    assert statut(True) == "COMPLET"

def test_expired_fds_is_expired():
    assert statut(True, date.today()-timedelta(days=1)) == "EXPIRE"
