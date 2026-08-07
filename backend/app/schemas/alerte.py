from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlerteLogistiqueRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cle: str
    categorie: str
    niveau: str
    titre: str
    message: str
    lien: str | None
    source_type: str | None
    source_id: int | None
    statut: str
    date_premiere_detection: datetime
    date_derniere_detection: datetime
    date_resolution: datetime | None
    acquittee_par: str | None
    date_acquittement: datetime | None


class ResumeAlertesRead(BaseModel):
    actives: int
    critiques: int
    avertissements: int
    acquittees: int
