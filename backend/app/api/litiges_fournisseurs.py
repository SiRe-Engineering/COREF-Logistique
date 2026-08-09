from datetime import date,datetime,timezone
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.litige_fournisseur import LitigeFournisseur
from app.models.non_conformite_fournisseur import NonConformiteFournisseur
from app.models.reception_achat import ReceptionAchat
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement

router=APIRouter(prefix="/api/litiges-fournisseurs",tags=["Retours et litiges fournisseurs"])
TYPES={"RETOUR_FOURNISSEUR","REMPLACEMENT","AVOIR","TRI","ACCEPTE_EN_ETAT"}

class Create(BaseModel):
    ncf_id:int
    commentaire:str|None=None
class Retour(BaseModel):
    quantite:Decimal=Field(gt=0)
    emplacement_source_id:int
    commentaire:str|None=None
class Avoir(BaseModel):
    reference_avoir:str=Field(min_length=1,max_length=120)
    montant_avoir_ht:Decimal=Field(ge=0)
    date_avoir:date
class Tri(BaseModel):
    quantite_conforme:Decimal=Field(ge=0)
    quantite_rebut:Decimal=Field(ge=0)
    emplacement_source_id:int|None=None
    commentaire:str|None=None
class Remplacement(BaseModel):
    reception_remplacement_id:int
class Commentaire(BaseModel):
    commentaire:str|None=None

def serial(l):
    n=l.ncf;r=n.reception
    return {"id":l.id,"reference":l.reference,"ncf_id":n.id,"ncf_reference":n.reference,
      "type_traitement":l.type_traitement,"statut":l.statut,"fournisseur":r.commande.fournisseur.raison_sociale,
      "commande_reference":r.commande.reference,"article_id":r.article_id,"article_reference":r.article.reference,
      "article_designation":r.article.designation,"lot_id":r.lot_beton_id,
      "lot_reference":r.lot_beton.reference_interne if r.lot_beton else None,"unite":r.article.unite,
      "quantite_ncf":n.quantite_concernee,"quantite_retour":l.quantite_retour,
      "emplacement_source_id":l.emplacement_source_id,
      "emplacement_source":l.emplacement_source.nom if l.emplacement_source else None,
      "date_retour":l.date_retour,"reference_avoir":l.reference_avoir,"montant_avoir_ht":l.montant_avoir_ht,
      "date_avoir":l.date_avoir,"reception_remplacement_id":l.reception_remplacement_id,
      "quantite_conforme_tri":l.quantite_conforme_tri,"quantite_rebut_tri":l.quantite_rebut_tri,
      "commentaire":l.commentaire,"date_creation":l.date_creation,"date_cloture":l.date_cloture}

def get_litige(db,id):
    x=db.get(LitigeFournisseur,id)
    if not x: raise HTTPException(404,"Litige fournisseur introuvable.")
    return x

@router.get("")
def liste(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return [serial(x) for x in db.scalars(select(LitigeFournisseur).order_by(LitigeFournisseur.date_creation.desc())).unique().all()]

@router.post("")
def creer(p:Create,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    n=db.get(NonConformiteFournisseur,p.ncf_id)
    if not n: raise HTTPException(404,"NCF introuvable.")
    if not n.decision or n.decision not in TYPES: raise HTTPException(422,"Définissez d'abord une décision de traitement sur la NCF.")
    if db.scalar(select(LitigeFournisseur.id).where(LitigeFournisseur.ncf_id==n.id)): raise HTTPException(409,"Un dossier de traitement existe déjà pour cette NCF.")
    nxt=(db.scalar(select(func.max(LitigeFournisseur.id))) or 0)+1
    statut={"RETOUR_FOURNISSEUR":"A_RETOURNER","REMPLACEMENT":"A_RETOURNER","AVOIR":"AVOIR_ATTENDU","TRI":"TRI_A_FAIRE","ACCEPTE_EN_ETAT":"CLOTURE"}[n.decision]
    x=LitigeFournisseur(reference=f"RET-{nxt:06d}",ncf_id=n.id,type_traitement=n.decision,statut=statut,commentaire=p.commentaire,cree_par=u.nom_complet)
    if statut=="CLOTURE": x.date_cloture=datetime.now(timezone.utc);n.statut="CLOTUREE";n.date_cloture=x.date_cloture
    db.add(x);db.commit();db.refresh(x);return serial(x)

@router.post("/{id}/retour")
def retour(id:int,p:Retour,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    x=get_litige(db,id);n=x.ncf;r=n.reception
    if x.type_traitement not in {"RETOUR_FOURNISSEUR","REMPLACEMENT"}: raise HTTPException(422,"Ce dossier ne nécessite pas de retour fournisseur.")
    if x.date_retour: raise HTTPException(409,"Le retour physique a déjà été validé.")
    if p.quantite>n.quantite_concernee: raise HTTPException(422,"La quantité retournée dépasse la quantité de la NCF.")
    stock=db.scalar(select(Stock).where(Stock.article_id==r.article_id,Stock.emplacement_id==p.emplacement_source_id))
    if not stock or stock.quantite_disponible<p.quantite: raise HTTPException(422,"Stock disponible insuffisant sur cet emplacement.")
    m=executer_mouvement(db,MouvementCreate(type="SORTIE",article_id=r.article_id,lot_id=r.lot_beton_id,
      emplacement_source_id=p.emplacement_source_id,quantite=p.quantite,motif=f"Retour fournisseur {x.reference}",
      commentaire=p.commentaire or x.commentaire,operateur=u.nom_complet,sortie_libre=True),valider_transaction=False)
    x.quantite_retour=p.quantite;x.emplacement_source_id=p.emplacement_source_id;x.date_retour=datetime.now(timezone.utc);x.mouvement_sortie_id=m.id
    x.statut="EN_ATTENTE_REMPLACEMENT" if x.type_traitement=="REMPLACEMENT" else "RETOURNE"
    if x.type_traitement=="RETOUR_FOURNISSEUR": n.statut="EN_TRAITEMENT"
    db.commit();db.refresh(x);return serial(x)

@router.post("/{id}/avoir")
def avoir(id:int,p:Avoir,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=get_litige(db,id)
    if x.type_traitement not in {"AVOIR","RETOUR_FOURNISSEUR"}: raise HTTPException(422,"Avoir non prévu pour ce dossier.")
    x.reference_avoir=p.reference_avoir;x.montant_avoir_ht=p.montant_avoir_ht;x.date_avoir=p.date_avoir
    x.statut="AVOIR_RECU"
    if x.type_traitement=="AVOIR": x.statut="CLOTURE";x.date_cloture=datetime.now(timezone.utc);x.ncf.statut="CLOTUREE";x.ncf.date_cloture=x.date_cloture
    db.commit();db.refresh(x);return serial(x)

@router.post("/{id}/tri")
def tri(id:int,p:Tri,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    x=get_litige(db,id);n=x.ncf;r=n.reception
    if x.type_traitement!="TRI": raise HTTPException(422,"Ce dossier n'est pas un tri.")
    if p.quantite_conforme+p.quantite_rebut!=n.quantite_concernee: raise HTTPException(422,"Conforme + rebut doit être égal à la quantité concernée par la NCF.")
    if p.quantite_rebut>0:
        if not p.emplacement_source_id: raise HTTPException(422,"Un emplacement est obligatoire pour sortir le rebut.")
        m=executer_mouvement(db,MouvementCreate(type="AJUSTEMENT_NEGATIF",article_id=r.article_id,lot_id=r.lot_beton_id,
          emplacement_source_id=p.emplacement_source_id,quantite=p.quantite_rebut,motif=f"Rebut après tri {x.reference}",
          commentaire=p.commentaire,operateur=u.nom_complet),valider_transaction=False)
        x.mouvement_sortie_id=m.id;x.emplacement_source_id=p.emplacement_source_id
    x.quantite_conforme_tri=p.quantite_conforme;x.quantite_rebut_tri=p.quantite_rebut;x.commentaire=p.commentaire
    x.statut="CLOTURE";x.date_cloture=datetime.now(timezone.utc);n.statut="CLOTUREE";n.date_cloture=x.date_cloture
    db.commit();db.refresh(x);return serial(x)

@router.post("/{id}/remplacement")
def remplacement(id:int,p:Remplacement,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=get_litige(db,id);n=x.ncf
    if x.type_traitement!="REMPLACEMENT": raise HTTPException(422,"Ce dossier n'est pas un remplacement.")
    if not x.date_retour: raise HTTPException(422,"Validez d'abord le retour physique.")
    r=db.get(ReceptionAchat,p.reception_remplacement_id)
    if not r or r.article_id!=n.reception.article_id or r.commande.fournisseur_id!=n.reception.commande.fournisseur_id:
        raise HTTPException(422,"La réception de remplacement doit concerner le même article et le même fournisseur.")
    if r.quantite<(x.quantite_retour or n.quantite_concernee): raise HTTPException(422,"La quantité réceptionnée est insuffisante pour solder le remplacement.")
    x.reception_remplacement_id=r.id;x.statut="CLOTURE";x.date_cloture=datetime.now(timezone.utc);n.statut="CLOTUREE";n.date_cloture=x.date_cloture
    db.commit();db.refresh(x);return serial(x)

@router.post("/{id}/cloture")
def cloture(id:int,p:Commentaire,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=get_litige(db,id)
    if x.type_traitement=="REMPLACEMENT" and not x.reception_remplacement_id: raise HTTPException(422,"Le remplacement n'a pas encore été réceptionné.")
    if x.type_traitement=="RETOUR_FOURNISSEUR" and not x.date_retour: raise HTTPException(422,"Le retour physique n'a pas encore été validé.")
    x.commentaire=p.commentaire or x.commentaire;x.statut="CLOTURE";x.date_cloture=datetime.now(timezone.utc);x.ncf.statut="CLOTUREE";x.ncf.date_cloture=x.date_cloture
    db.commit();db.refresh(x);return serial(x)
