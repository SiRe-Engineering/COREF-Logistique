from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AffairePreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    code_externe: str | None
    nom: str
    client: str | None
    site: str | None
    zone_intervention: str | None
    charge_affaires: str | None
    date_debut: date | None
    date_fin_prevue: date | None


class ArticlePreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    designation: str
    unite: str


class LotPreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference_interne: str
    numero_lot_fournisseur: str
    date_peremption: date


class EmplacementPreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    nom: str


class LignePreparationCreate(BaseModel):
    article_id: int
    lot_id: int | None = None
    emplacement_source_id: int | None = None
    quantite_demandee: Decimal = Field(gt=0)
    commentaire: str | None = Field(default=None, max_length=255)


class PropositionRemplacementCreate(BaseModel):
    article_remplacement_id: int
    lot_remplacement_id: int | None = None
    emplacement_remplacement_id: int
    quantite_remplacement: Decimal = Field(gt=0)
    commentaire_remplacement: str = Field(min_length=3, max_length=1000)


class DecisionRemplacementCreate(BaseModel):
    commentaire_decision: str | None = Field(default=None, max_length=1000)


class LignePreparationUpdate(BaseModel):
    lot_id: int | None = None
    emplacement_source_id: int | None = None
    quantite_demandee: Decimal | None = Field(default=None, gt=0)
    quantite_preparee: Decimal | None = Field(default=None, ge=0)
    statut: str | None = Field(default=None, max_length=30)
    commentaire: str | None = Field(default=None, max_length=255)
    motif_ecart: str | None = Field(default=None, max_length=500)


class LignePreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    lot_id: int | None
    emplacement_source_id: int | None
    quantite_demandee: Decimal
    quantite_preparee: Decimal
    quantite_manquante: Decimal
    statut: str
    commentaire: str | None
    motif_ecart: str | None
    date_debut_preparation: datetime | None
    date_fin_preparation: datetime | None
    article_remplacement_id: int | None
    lot_remplacement_id: int | None
    emplacement_remplacement_id: int | None
    quantite_remplacement: Decimal | None
    commentaire_remplacement: str | None
    propose_par: str | None
    date_proposition_remplacement: datetime | None
    decision_remplacement: str | None
    decision_par: str | None
    commentaire_decision: str | None
    date_decision_remplacement: datetime | None
    article_remplacement: ArticlePreparationRead | None
    lot_remplacement: LotPreparationRead | None
    emplacement_remplacement: EmplacementPreparationRead | None
    article: ArticlePreparationRead
    lot: LotPreparationRead | None
    emplacement_source: EmplacementPreparationRead | None


class PreparationCreate(BaseModel):
    affaire_id: int
    nom: str = Field(min_length=1, max_length=200)
    date_besoin: date | None = None
    demandeur: str | None = Field(default=None, max_length=120)
    preparateur: str | None = Field(default=None, max_length=120)
    vehicule: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None


class PreparationUpdate(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=200)
    date_besoin: date | None = None
    demandeur: str | None = Field(default=None, max_length=120)
    preparateur: str | None = Field(default=None, max_length=120)
    vehicule: str | None = Field(default=None, max_length=120)
    commentaire: str | None = None


class PreparationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    affaire_id: int
    nom: str
    statut: str
    date_besoin: date | None
    demandeur: str | None
    preparateur: str | None
    vehicule: str | None
    commentaire: str | None
    date_creation: datetime
    date_validation: datetime | None
    date_expedition: datetime | None
    affaire: AffairePreparationRead
    lignes: list[LignePreparationRead] = []



class LigneRetourDisponibleRead(BaseModel):
    ligne_preparation_id: int
    article_id: int
    lot_id: int | None
    article: ArticlePreparationRead
    lot: LotPreparationRead | None
    quantite_expediee: Decimal
    quantite_deja_retournee: Decimal
    quantite_retournable: Decimal


class LigneRetourCreate(BaseModel):
    ligne_preparation_id: int
    emplacement_destination_id: int
    quantite: Decimal = Field(gt=0)
    commentaire: str | None = Field(default=None, max_length=500)


class RetourPreparationCreate(BaseModel):
    lignes: list[LigneRetourCreate] = Field(min_length=1)
    operateur: str | None = Field(default=None, max_length=120)


class RetourPreparationRead(BaseModel):
    preparation_id: int
    reference_preparation: str
    mouvements_crees: int
    quantite_totale_retournee: Decimal
