from datetime import datetime,timezone
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.non_conformite_fournisseur import NonConformiteFournisseur
from app.models.reception_achat import ReceptionAchat
from app.models.litige_fournisseur import LitigeFournisseur
from app.models.utilisateur import Utilisateur

router=APIRouter(prefix="/api/non-conformites-fournisseurs",tags=["Non-conformités fournisseurs"])
DECISIONS={"ACCEPTE_EN_ETAT","TRI","RETOUR_FOURNISSEUR","REMPLACEMENT","AVOIR"}
STATUTS={"OUVERTE","EN_TRAITEMENT","CLOTUREE"}

class Create(BaseModel):
    reception_id:int
    quantite_concernee:Decimal=Field(gt=0)
    description:str=Field(min_length=3)
    responsable:str|None=None

class Update(BaseModel):
    decision:str|None=None
    responsable:str|None=None
    statut:str|None=None
    commentaire_traitement:str|None=None

def serialize(n):
    r=n.reception
    return {"id":n.id,"reference":n.reference,"reception_id":n.reception_id,
      "commande_reference":r.commande.reference,"fournisseur_id":r.commande.fournisseur_id,
      "fournisseur":r.commande.fournisseur.raison_sociale,
      "article_reference":r.article.reference,"article_designation":r.article.designation,
      "lot_reference":r.lot_beton.reference_interne if r.lot_beton else None,
      "quantite_recue":r.quantite,"quantite_concernee":n.quantite_concernee,
      "unite":r.article.unite,"description":n.description,"decision":n.decision,
      "responsable":n.responsable,"statut":n.statut,
      "commentaire_traitement":n.commentaire_traitement,
      "date_creation":n.date_creation,"date_cloture":n.date_cloture,"cree_par":n.cree_par,
      "litige_reference": next((x.reference for x in n.litiges),None) if hasattr(n,"litiges") else None}

@router.get("")
def list_all(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return [serialize(x) for x in db.scalars(select(NonConformiteFournisseur).order_by(NonConformiteFournisseur.date_creation.desc())).unique().all()]

@router.post("")
def create(p:Create,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    r=db.get(ReceptionAchat,p.reception_id)
    if not r: raise HTTPException(404,"Réception introuvable.")
    if p.quantite_concernee>r.quantite: raise HTTPException(422,"La quantité non conforme ne peut pas dépasser la quantité réceptionnée.")
    if db.scalar(select(NonConformiteFournisseur.id).where(NonConformiteFournisseur.reception_id==r.id)):
        raise HTTPException(409,"Une non-conformité existe déjà pour cette réception.")
    nxt=(db.scalar(select(func.max(NonConformiteFournisseur.id))) or 0)+1
    n=NonConformiteFournisseur(reference=f"NCF-{nxt:06d}",reception_id=r.id,quantite_concernee=p.quantite_concernee,
      description=p.description.strip(),responsable=p.responsable,statut="OUVERTE",cree_par=u.nom_complet)
    db.add(n);db.flush();db.commit();db.refresh(n)
    return serialize(n)

@router.patch("/{ncf_id}")
def update(ncf_id:int,p:Update,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    n=db.get(NonConformiteFournisseur,ncf_id)
    if not n: raise HTTPException(404,"Non-conformité introuvable.")
    if p.decision is not None:
        if p.decision not in DECISIONS: raise HTTPException(422,"Décision invalide.")
        n.decision=p.decision
    if p.statut is not None:
        if p.statut not in STATUTS: raise HTTPException(422,"Statut invalide.")
        if p.statut=="CLOTUREE" and not (p.decision or n.decision): raise HTTPException(422,"Une décision est obligatoire avant clôture.")
        n.statut=p.statut;n.date_cloture=datetime.now(timezone.utc) if p.statut=="CLOTUREE" else None
    if p.responsable is not None:n.responsable=p.responsable or None
    if p.commentaire_traitement is not None:n.commentaire_traitement=p.commentaire_traitement or None
    db.commit();db.refresh(n);return serialize(n)
