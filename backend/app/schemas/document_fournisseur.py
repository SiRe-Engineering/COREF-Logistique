from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


TypeDocument = Literal[
    "CERTIFICAT",
    "FDS",
    "FICHE_TECHNIQUE",
    "BON_LIVRAISON",
    "AUTRE",
]


class DocumentCreate(BaseModel):
    type_document: TypeDocument
    nom_fichier: str = Field(min_length=1, max_length=255)
    type_mime: str = Field(min_length=1, max_length=120)
    contenu_base64: str = Field(min_length=1)
    lot_beton_id: int | None = None
    fournisseur_id: int | None = None
    commande_achat_id: int | None = None
    article_id: int | None = None
    reference_document: str | None = Field(default=None, max_length=255)
    date_document: date | None = None
    date_expiration: date | None = None
    commentaire: str | None = None

    @model_validator(mode="after")
    def valider_cible(self):
        if not any(
            [
                self.lot_beton_id,
                self.fournisseur_id,
                self.commande_achat_id,
                self.article_id,
            ]
        ):
            raise ValueError(
                "Le document doit être rattaché à un lot, fournisseur, "
                "commande ou article."
            )
        if (
            self.date_document
            and self.date_expiration
            and self.date_expiration < self.date_document
        ):
            raise ValueError(
                "La date d'expiration ne peut pas précéder la date du document."
            )
        return self


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type_document: str
    nom_fichier: str
    type_mime: str
    taille_octets: int
    lot_beton_id: int | None
    fournisseur_id: int | None
    commande_achat_id: int | None
    article_id: int | None
    reference_document: str | None
    date_document: date | None
    date_expiration: date | None
    commentaire: str | None
    depose_par: str | None
    date_depot: datetime


class StatutDocumentaireLotRead(BaseModel):
    lot_id: int
    reference_interne: str
    article_reference: str
    article_designation: str
    certificat_present: bool
    fds_presente: bool
    document_expire: bool
    statut: str
    documents: list[DocumentRead]
