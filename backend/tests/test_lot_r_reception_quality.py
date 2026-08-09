def statut(conformite, beton=False, fds=True):
    if conformite=="NON_CONFORME": return "NON_CONFORME"
    if conformite=="RESERVE": return "SOUS_RESERVE"
    if beton and not fds: return "A_CONTROLER"
    return "CONFORME"

def test_beton_without_fds_is_flagged_not_blocked():
    assert statut("CONFORME",beton=True,fds=False)=="A_CONTROLER"

def test_visual_nonconformity_has_priority():
    assert statut("NON_CONFORME",beton=True,fds=False)=="NON_CONFORME"
