from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.intervention_materiel import InterventionMateriel
from app.models.materiel import Materiel
from app.models.pret_materiel import PretMateriel
from app.models.utilisateur import Utilisateur

router=APIRouter(prefix="/api/maintenance-materiel",tags=["Maintenance matériel"])
TYPES={"PREVENTIVE","CORRECTIVE","CONTROLE_PERIODIQUE","ETALONNAGE","AUTRE"}
STATUTS={"A_PLANIFIER","PLANIFIEE","EN_COURS","TERMINEE","ANNULEE"}

class Create(BaseModel):
    materiel_id:int
    type_intervention:str
    description:str=Field(min_length=3)
    date_planifiee:date|None=None
    prestataire:str|None=None

class Update(BaseModel):
    statut:str|None=None
    date_planifiee:date|None=None
    diagnostic:str|None=None
    action_realisee:str|None=None
    prestataire:str|None=None
    cout_ht:Decimal|None=Field(default=None,ge=0)
    prochain_controle:date|None=None

def serial(x):
    m=x.materiel
    return {"id":x.id,"reference":x.reference,"materiel_id":m.id,"numero_inventaire":m.numero_inventaire,
      "designation":m.designation,"categorie":m.categorie,"type_intervention":x.type_intervention,
      "statut":x.statut,"date_signalement":x.date_signalement,"date_planifiee":x.date_planifiee,
      "date_debut":x.date_debut,"date_fin":x.date_fin,"description":x.description,
      "diagnostic":x.diagnostic,"action_realisee":x.action_realisee,"prestataire":x.prestataire,
      "cout_ht":x.cout_ht,"prochain_controle":x.prochain_controle,"cree_par":x.cree_par,
      "materiel_etat":m.etat,"date_prochain_controle_materiel":m.date_prochain_controle}

@router.get("")
def lister(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return [serial(x) for x in db.scalars(select(InterventionMateriel).order_by(InterventionMateriel.date_signalement.desc())).unique().all()]

@router.get("/dashboard")
def dashboard(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    today=date.today();horizon=today+timedelta(days=30)
    mats=list(db.scalars(select(Materiel).where(Materiel.actif.is_(True)).order_by(Materiel.numero_inventaire)).all())
    ouverts=list(db.scalars(select(InterventionMateriel).where(InterventionMateriel.statut.notin_(["TERMINEE","ANNULEE"]))).unique().all())
    retards=[m for m in mats if m.date_prochain_controle and m.date_prochain_controle<today]
    proches=[m for m in mats if m.date_prochain_controle and today<=m.date_prochain_controle<=horizon]
    return {
      "interventions_ouvertes":len(ouverts),
      "materiels_en_maintenance":sum(1 for m in mats if m.etat=="EN_MAINTENANCE"),
      "controles_en_retard":len(retards),
      "controles_30_jours":len(proches),
      "controles":[{"materiel_id":m.id,"numero_inventaire":m.numero_inventaire,"designation":m.designation,
         "date_prochain_controle":m.date_prochain_controle,
         "statut":"EN_RETARD" if m.date_prochain_controle<today else "A_VENIR"} for m in sorted(retards+proches,key=lambda x:x.date_prochain_controle)]
    }

@router.post("")
def creer(p:Create,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    if p.type_intervention not in TYPES: raise HTTPException(422,"Type d'intervention invalide.")
    m=db.scalar(select(Materiel).where(Materiel.id==p.materiel_id).with_for_update(of=Materiel))
    if not m or not m.actif: raise HTTPException(404,"Matériel introuvable.")
    pret=db.scalar(select(PretMateriel.id).where(PretMateriel.materiel_id==m.id,PretMateriel.date_retour_reelle.is_(None)))
    if pret and p.type_intervention in {"CORRECTIVE","CONTROLE_PERIODIQUE","ETALONNAGE"}:
        raise HTTPException(409,"Le matériel est actuellement en déplacement. Enregistrez d'abord son retour.")
    nxt=(db.scalar(select(func.max(InterventionMateriel.id))) or 0)+1
    statut="PLANIFIEE" if p.date_planifiee else "A_PLANIFIER"
    x=InterventionMateriel(reference=f"MAINT-{nxt:06d}",materiel_id=m.id,type_intervention=p.type_intervention,
      statut=statut,description=p.description.strip(),date_planifiee=p.date_planifiee,prestataire=p.prestataire,cree_par=u.nom_complet)
    db.add(x);db.commit();db.refresh(x);return serial(x)

@router.patch("/{id}")
def modifier(id:int,p:Update,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    x=db.scalar(select(InterventionMateriel).where(InterventionMateriel.id==id).with_for_update(of=InterventionMateriel))
    if not x: raise HTTPException(404,"Intervention introuvable.")
    m=db.scalar(select(Materiel).where(Materiel.id==x.materiel_id).with_for_update(of=Materiel))
    if p.statut:
        if p.statut not in STATUTS: raise HTTPException(422,"Statut invalide.")
        if p.statut=="EN_COURS":
            x.date_debut=x.date_debut or datetime.now(timezone.utc)
            m.etat="EN_MAINTENANCE"
        elif p.statut=="TERMINEE":
            if not (p.action_realisee or x.action_realisee): raise HTTPException(422,"L'action réalisée est obligatoire pour terminer l'intervention.")
            x.date_fin=datetime.now(timezone.utc)
            m.etat="DISPONIBLE"
        elif p.statut=="ANNULEE":
            if m.etat=="EN_MAINTENANCE": m.etat="DISPONIBLE"
        x.statut=p.statut
    for k in ["date_planifiee","diagnostic","action_realisee","prestataire","cout_ht","prochain_controle"]:
        v=getattr(p,k)
        if v is not None: setattr(x,k,v)
    if p.prochain_controle is not None:
        m.date_prochain_controle=p.prochain_controle
        m.date_dernier_controle=date.today()
    db.commit();db.refresh(x);return serial(x)
