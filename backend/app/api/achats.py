from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.achats import Fournisseur, ArticleFournisseur, CommandeAchat, LigneCommandeAchat
from app.models.article import Article
from app.models.reapprovisionnement import BesoinReapprovisionnement
from app.models.utilisateur import Utilisateur
from app.schemas.achats import *
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement

router=APIRouter(prefix="/api/achats",tags=["Achats fournisseurs"])

def _commande(db:Session,id:int)->CommandeAchat:
    c=db.scalar(select(CommandeAchat).options(selectinload(CommandeAchat.lignes)).where(CommandeAchat.id==id))
    if not c: raise HTTPException(404,"Commande introuvable.")
    return c

@router.get("/fournisseurs",response_model=list[FournisseurRead])
def fournisseurs(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return list(db.scalars(select(Fournisseur).order_by(Fournisseur.raison_sociale)).all())

@router.post("/fournisseurs",response_model=FournisseurRead,status_code=201)
def creer_fournisseur(
    p: FournisseurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    donnees = p.model_dump()
    donnees["code"] = p.code.strip().upper()

    f = Fournisseur(**donnees)
    db.add(f)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code fournisseur existe déjà.",
        )

    db.refresh(f)
    return f

@router.patch("/fournisseurs/{id}",response_model=FournisseurRead)
def modifier_fournisseur(id:int,p:FournisseurUpdate,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    f=db.get(Fournisseur,id)
    if not f: raise HTTPException(404,"Fournisseur introuvable.")
    for k,v in p.model_dump(exclude_unset=True).items():
        if k=="code" and v: v=v.strip().upper()
        setattr(f,k,v)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,"Ce code fournisseur existe déjà.")
    db.refresh(f); return f

@router.get("/articles-fournisseurs",response_model=list[ArticleFournisseurRead])
def liens(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return list(db.scalars(select(ArticleFournisseur).order_by(ArticleFournisseur.article_id)).unique().all())

@router.post("/articles-fournisseurs",response_model=ArticleFournisseurRead,status_code=201)
def lier(p:ArticleFournisseurCreate,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    if not db.get(Article,p.article_id) or not db.get(Fournisseur,p.fournisseur_id):
        raise HTTPException(404,"Article ou fournisseur introuvable.")
    if p.fournisseur_prefere:
        for x in db.scalars(select(ArticleFournisseur).where(ArticleFournisseur.article_id==p.article_id)).all():
            x.fournisseur_prefere=False
    x=ArticleFournisseur(**p.model_dump(),date_maj_prix=datetime.now(timezone.utc) if p.prix_unitaire_ht is not None else None)
    db.add(x)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,"Ce fournisseur est déjà associé à cet article.")
    db.refresh(x); return x

@router.get("/commandes",response_model=list[CommandeRead])
def commandes(db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    return list(db.scalars(select(CommandeAchat).options(selectinload(CommandeAchat.lignes)).order_by(CommandeAchat.date_creation.desc())).unique().all())

@router.post("/commandes",response_model=CommandeRead,status_code=201)
def creer_commande(p:CommandeCreate,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    f=db.get(Fournisseur,p.fournisseur_id)
    if not f or not f.actif: raise HTTPException(404,"Fournisseur introuvable ou inactif.")
    c=CommandeAchat(fournisseur_id=f.id,date_livraison_prevue=p.date_livraison_prevue,commentaire=p.commentaire,cree_par=u.nom_complet)
    db.add(c); db.flush()
    for lp in p.lignes:
        a=db.get(Article,lp.article_id)
        if not a or not a.actif: raise HTTPException(404,f"Article {lp.article_id} introuvable.")
        b=None
        if lp.besoin_reapprovisionnement_id:
            b=db.get(BesoinReapprovisionnement,lp.besoin_reapprovisionnement_id)
            if not b or b.article_id!=a.id: raise HTTPException(422,"Besoin incohérent avec l'article.")
            if b.statut in {"RECU","ANNULE"}: raise HTTPException(409,f"Le besoin {b.reference} est clôturé.")
        ligne=LigneCommandeAchat(commande_id=c.id,**lp.model_dump())
        db.add(ligne)
        if b:
            b.quantite_commandee=lp.quantite_commandee
            b.prix_unitaire_prevu=lp.prix_unitaire_ht
            b.fournisseur=f.raison_sociale
            b.reference_commande=c.reference
            b.statut="COMMANDE"
            b.date_commande=datetime.now(timezone.utc)
    db.commit(); db.refresh(c); return _commande(db,c.id)

@router.patch("/commandes/{id}",response_model=CommandeRead)
def modifier_commande(id:int,p:CommandeUpdate,db:Session=Depends(get_db),_:Utilisateur=Depends(utilisateur_courant)):
    c=_commande(db,id)
    if c.statut in {"RECUE","ANNULEE"}: raise HTTPException(409,"Cette commande est clôturée.")
    old=c.statut
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(c,k,v)
    if c.statut=="ENVOYEE" and old!="ENVOYEE": c.date_commande=datetime.now(timezone.utc)
    db.commit(); return _commande(db,id)

@router.post("/commandes/{commande_id}/lignes/{ligne_id}/reception",response_model=CommandeRead)
def reception(commande_id:int,ligne_id:int,p:ReceptionLigneCreate,db:Session=Depends(get_db),u:Utilisateur=Depends(utilisateur_courant)):
    c=_commande(db,commande_id)
    if c.statut in {"BROUILLON","ANNULEE","RECUE"}: raise HTTPException(409,"La commande n'est pas réceptionnable dans cet état.")
    l=next((x for x in c.lignes if x.id==ligne_id),None)
    if not l: raise HTTPException(404,"Ligne de commande introuvable.")
    restant=l.quantite_commandee-l.quantite_recue
    if p.quantite>restant: raise HTTPException(422,f"Réception supérieure au solde attendu ({restant}).")
    prix=p.prix_unitaire_ht if p.prix_unitaire_ht is not None else l.prix_unitaire_ht
    executer_mouvement(db,MouvementCreate(
        type="ENTREE",article_id=l.article_id,lot_id=p.lot_id,
        besoin_reapprovisionnement_id=l.besoin_reapprovisionnement_id,
        ligne_commande_achat_id=l.id,
        emplacement_destination_id=p.emplacement_destination_id,
        quantite=p.quantite,prix_unitaire_ht=prix,
        motif=f"Réception {c.reference}",commentaire=p.commentaire,operateur=u.nom_complet
    ),valider_transaction=False)
    l.quantite_recue+=p.quantite
    if l.besoin:
        l.besoin.quantite_recue+=p.quantite
        if l.besoin.quantite_recue>=l.besoin.quantite_commandee:
            l.besoin.statut="RECU"; l.besoin.date_cloture=datetime.now(timezone.utc)
    total=sum((x.quantite_commandee for x in c.lignes),start=0)
    recu=sum((x.quantite_recue for x in c.lignes),start=0)
    c.statut="RECUE" if recu>=total else "PARTIELLEMENT_RECUE"
    db.commit(); return _commande(db,c.id)
