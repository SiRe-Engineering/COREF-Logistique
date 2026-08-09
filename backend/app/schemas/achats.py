from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

StatutCommande = Literal["BROUILLON","VALIDEE","ENVOYEE","PARTIELLEMENT_RECUE","RECUE","ANNULEE"]

class FournisseurCreate(BaseModel):
    code: str = Field(min_length=2,max_length=30)
    raison_sociale: str = Field(min_length=2,max_length=180)
    contact: str | None = None
    email: str | None = None
    telephone: str | None = None
    adresse: str | None = None
    conditions_paiement: str | None = None
    delai_habituel_jours: int | None = Field(default=None,ge=0)
    commentaire: str | None = None

class FournisseurUpdate(BaseModel):
    code: str | None = Field(default=None,min_length=2,max_length=30)
    raison_sociale: str | None = Field(default=None,min_length=2,max_length=180)
    contact: str | None = None
    email: str | None = None
    telephone: str | None = None
    adresse: str | None = None
    conditions_paiement: str | None = None
    delai_habituel_jours: int | None = Field(default=None,ge=0)
    commentaire: str | None = None
    actif: bool | None = None

class FournisseurRead(FournisseurCreate):
    model_config=ConfigDict(from_attributes=True)
    id:int
    actif:bool
    date_creation:datetime
    date_modification:datetime

class ArticleSimple(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; reference:str; designation:str; unite:str

class ArticleFournisseurCreate(BaseModel):
    article_id:int
    fournisseur_id:int
    reference_fournisseur:str|None=None
    prix_unitaire_ht:Decimal|None=Field(default=None,ge=0)
    delai_jours:int|None=Field(default=None,ge=0)
    minimum_commande:Decimal|None=Field(default=None,ge=0)
    fournisseur_prefere:bool=False

class ArticleFournisseurRead(ArticleFournisseurCreate):
    model_config=ConfigDict(from_attributes=True)
    id:int
    date_maj_prix:datetime|None
    article:ArticleSimple
    fournisseur:FournisseurRead

class LigneCommandeCreate(BaseModel):
    article_id:int
    besoin_reapprovisionnement_id:int|None=None
    quantite_commandee:Decimal=Field(gt=0)
    prix_unitaire_ht:Decimal=Field(ge=0)
    reference_fournisseur:str|None=None

class CommandeCreate(BaseModel):
    fournisseur_id:int
    date_livraison_prevue:date|None=None
    commentaire:str|None=None
    lignes:list[LigneCommandeCreate]=Field(min_length=1)

class CommandeUpdate(BaseModel):
    statut:StatutCommande|None=None
    reference_fournisseur:str|None=None
    date_livraison_prevue:date|None=None
    commentaire:str|None=None

class LigneCommandeRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; article_id:int; besoin_reapprovisionnement_id:int|None
    reference_fournisseur:str|None
    quantite_commandee:Decimal; quantite_recue:Decimal; prix_unitaire_ht:Decimal
    date_premiere_reception:datetime|None; date_derniere_reception:datetime|None
    article:ArticleSimple

class CommandeRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; reference:str; fournisseur_id:int; statut:str
    reference_fournisseur:str|None; date_commande:datetime|None
    date_livraison_prevue:date|None; commentaire:str|None; cree_par:str|None
    date_premiere_reception:datetime|None; date_reception_finale:datetime|None
    date_creation:datetime; date_modification:datetime
    fournisseur:FournisseurRead
    lignes:list[LigneCommandeRead]

class ReceptionLigneCreate(BaseModel):
    quantite:Decimal=Field(gt=0)
    emplacement_destination_id:int
    lot_id:int|None=None
    prix_unitaire_ht:Decimal|None=Field(default=None,ge=0)
    commentaire:str|None=None
    bon_livraison_reference:str|None=Field(default=None,max_length=120)
    conformite_visuelle:Literal["CONFORME","RESERVE","NON_CONFORME"]="CONFORME"
    reserve_commentaire:str|None=None
    commentaire_qualite:str|None=None
    bon_livraison_nom_fichier:str|None=None
    bon_livraison_type_mime:str|None=None
    bon_livraison_contenu_base64:str|None=None

    @model_validator(mode="after")
    def valider_controle_qualite(self):
        if self.conformite_visuelle != "CONFORME" and not (
            self.reserve_commentaire and self.reserve_commentaire.strip()
        ):
            raise ValueError(
                "Un commentaire de réserve est obligatoire si la réception "
                "n'est pas conforme."
            )
        return self


class ReceptionLigneResult(BaseModel):
    commande: CommandeRead
    reception_id:int
    statut_qualite:str
    avertissements:list[str]=[]



class ArticleFournisseurUpdate(BaseModel):
    reference_fournisseur: str | None = None
    prix_unitaire_ht: Decimal | None = Field(default=None, ge=0)
    delai_jours: int | None = Field(default=None, ge=0)
    minimum_commande: Decimal | None = Field(default=None, ge=0)
    fournisseur_prefere: bool | None = None
    commentaire_prix: str | None = None


class HistoriquePrixFournisseurRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    article_fournisseur_id: int
    prix_unitaire_ht: Decimal
    date_effet: datetime
    modifie_par: str | None
    commentaire: str | None
