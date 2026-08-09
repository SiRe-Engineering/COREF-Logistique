from datetime import date,datetime,timezone
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field,model_validator
from sqlalchemy import func,select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.affaire import Affaire
from app.models.emplacement import Emplacement
from app.models.materiel import Materiel
from app.models.pret_materiel import PretMateriel
from app.models.utilisateur import Utilisateur

router=APIRouter(prefix="/api/prets-materiel",tags=["Prêts matériel"])

ETATS_RETOUR={"DISPONIBLE","EN_MAINTENANCE","HORS_SERVICE"}

class PretCreate(BaseModel):
    materiel_id:int
    emprunteur_id:int|None=None
    affaire_id:int|None=None
    site_zone:str|None=Field(default=None,max_length=180)
    date_retour_prevue:date
    commentaire_sortie:str|None=None

    @model_validator(mode="after")
    def cible(self):
        if self.emprunteur_id is None and self.affaire_id is None:
            raise ValueError("Sélectionnez un emprunteur ou une affaire.")
        return self

class RetourCreate(BaseModel):
    emplacement_retour_id:int
    etat_retour:str
    commentaire_retour:str|None=None

def serial(p:PretMateriel):
    today=date.today()
    if p.date_retour_reelle is not None:
        statut="RETOURNE"
    elif p.date_retour_prevue<today:
        statut="EN_RETARD"
    else:
        statut="EN_COURS"
    return {
        "id":p.id,"reference":p.reference,"statut":statut,
        "materiel_id":p.materiel_id,"numero_inventaire":p.materiel.numero_inventaire,
        "designation":p.materiel.designation,"categorie":p.materiel.categorie,
        "emprunteur_id":p.emprunteur_id,
        "emprunteur":p.emprunteur.nom_complet if p.emprunteur else None,
        "affaire_id":p.affaire_id,
        "affaire_reference":p.affaire.reference if p.affaire else None,
        "affaire_nom":p.affaire.nom if p.affaire else None,
        "site_zone":p.site_zone,"date_sortie":p.date_sortie,
        "date_retour_prevue":p.date_retour_prevue,
        "date_retour_reelle":p.date_retour_reelle,
        "etat_depart":p.etat_depart,"etat_retour":p.etat_retour,
        "emplacement_depart_id":p.emplacement_depart_id,
        "emplacement_depart":p.emplacement_depart.nom if p.emplacement_depart else None,
        "emplacement_retour_id":p.emplacement_retour_id,
        "emplacement_retour":p.emplacement_retour.nom if p.emplacement_retour else None,
        "commentaire_sortie":p.commentaire_sortie,
        "commentaire_retour":p.commentaire_retour,
        "cree_par":p.cree_par,
    }

@router.get("")
def lister(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return [serial(x) for x in db.scalars(select(PretMateriel).order_by(PretMateriel.date_sortie.desc())).unique().all()]

@router.get("/referentiels")
def referentiels(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    materiels=list(db.scalars(select(Materiel).where(Materiel.actif.is_(True)).order_by(Materiel.numero_inventaire)).unique().all())
    actifs={x.materiel_id for x in db.scalars(select(PretMateriel).where(PretMateriel.date_retour_reelle.is_(None))).all()}
    utilisateurs=list(db.scalars(select(Utilisateur).where(Utilisateur.actif.is_(True),Utilisateur.type_compte=="METIER",Utilisateur.entreprise=="COREF").order_by(Utilisateur.nom_complet)).all())
    affaires=list(db.scalars(select(Affaire).where(Affaire.actif.is_(True),Affaire.statut.notin_(["TERMINEE","ANNULEE"])).order_by(Affaire.reference.desc())).all())
    emplacements=list(db.scalars(select(Emplacement).where(Emplacement.actif.is_(True)).order_by(Emplacement.code)).all())
    return {
      "materiels":[{"id":m.id,"numero_inventaire":m.numero_inventaire,"designation":m.designation,"categorie":m.categorie,"etat":m.etat,"emplacement_id":m.emplacement_id,"disponible_pour_pret":m.id not in actifs and m.etat=="DISPONIBLE"} for m in materiels],
      "utilisateurs":[{"id":u.id,"nom_complet":u.nom_complet,"fonction":u.fonction} for u in utilisateurs],
      "affaires":[{"id":a.id,"reference":a.reference,"nom":a.nom,"client":a.client,"site":a.site} for a in affaires],
      "emplacements":[{"id":e.id,"code":e.code,"nom":e.nom} for e in emplacements],
    }

@router.post("")
def creer(p:PretCreate,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    if p.date_retour_prevue<date.today():
        raise HTTPException(422,"La date de retour prévue ne peut pas être passée.")
    m=db.scalar(select(Materiel).where(Materiel.id==p.materiel_id).with_for_update(of=Materiel))
    if not m or not m.actif: raise HTTPException(404,"Matériel introuvable.")
    if m.etat!="DISPONIBLE": raise HTTPException(409,f"Le matériel n'est pas disponible ({m.etat}).")
    if db.scalar(select(PretMateriel.id).where(PretMateriel.materiel_id==m.id,PretMateriel.date_retour_reelle.is_(None))):
        raise HTTPException(409,"Ce matériel possède déjà un prêt actif.")
    emprunteur=None
    if p.emprunteur_id:
        emprunteur=db.get(Utilisateur,p.emprunteur_id)
        if not emprunteur or not emprunteur.actif: raise HTTPException(404,"Emprunteur introuvable.")
    affaire=None
    if p.affaire_id:
        affaire=db.get(Affaire,p.affaire_id)
        if not affaire or not affaire.actif or affaire.statut in {"TERMINEE","ANNULEE"}: raise HTTPException(409,"Affaire indisponible.")
    nxt=(db.scalar(select(func.max(PretMateriel.id))) or 0)+1
    pret=PretMateriel(
      reference=f"PRET-{nxt:06d}",materiel_id=m.id,emprunteur_id=p.emprunteur_id,
      affaire_id=p.affaire_id,site_zone=p.site_zone,date_retour_prevue=p.date_retour_prevue,
      etat_depart=m.etat,emplacement_depart_id=m.emplacement_id,
      commentaire_sortie=p.commentaire_sortie,cree_par=u.nom_complet)
    db.add(pret)
    m.etat="EN_PRET"
    m.affaire_id=p.affaire_id
    try: db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,"Ce matériel possède déjà un prêt actif.")
    db.refresh(pret)
    return serial(pret)

@router.post("/{pret_id}/retour")
def retour(pret_id:int,p:RetourCreate,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    pret=db.scalar(select(PretMateriel).where(PretMateriel.id==pret_id).with_for_update(of=PretMateriel))
    if not pret: raise HTTPException(404,"Prêt introuvable.")
    if pret.date_retour_reelle is not None: raise HTTPException(409,"Ce prêt est déjà retourné.")
    if p.etat_retour not in ETATS_RETOUR: raise HTTPException(422,"État de retour invalide.")
    emp=db.get(Emplacement,p.emplacement_retour_id)
    if not emp or not emp.actif: raise HTTPException(404,"Emplacement de retour introuvable.")
    m=db.scalar(select(Materiel).where(Materiel.id==pret.materiel_id).with_for_update(of=Materiel))
    pret.date_retour_reelle=datetime.now(timezone.utc)
    pret.etat_retour=p.etat_retour
    pret.emplacement_retour_id=p.emplacement_retour_id
    pret.commentaire_retour=p.commentaire_retour
    m.etat=p.etat_retour
    m.emplacement_id=p.emplacement_retour_id
    m.affaire_id=None
    db.commit();db.refresh(pret)
    return serial(pret)
