from datetime import date, datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.article import Article
from app.models.emplacement import Emplacement
from app.models.stock import Stock
from app.models.utilisateur import Utilisateur
from app.models.mouvement import MouvementStock
from app.models.inventaire_avance import CampagneInventaireAvance, LigneInventaireAvance

router = APIRouter(prefix="/api/inventaires-avances", tags=["Inventaires avances"])

class CampagneCreate(BaseModel):
    libelle: str = Field(min_length=3, max_length=180)
    date_comptage: date | None = None
    commentaire: str | None = None
    emplacement_id: int | None = None
    famille_id: int | None = None

class Comptage(BaseModel):
    quantite_comptee: Decimal = Field(ge=0)
    justification: str | None = None

def ligne_json(x):
    ecart = None if x.quantite_comptee is None else x.quantite_comptee - x.quantite_theorique
    valeur = None if ecart is None else ecart * x.prix_unitaire
    return {
        "id": x.id,
        "article_id": x.article_id,
        "reference_article": x.article.reference,
        "designation": x.article.designation,
        "famille": getattr(getattr(x.article, "famille", None), "nom", None),
        "emplacement_id": x.emplacement_id,
        "emplacement": x.emplacement.nom,
        "quantite_theorique": x.quantite_theorique,
        "quantite_comptee": x.quantite_comptee,
        "ecart": ecart,
        "prix_unitaire": x.prix_unitaire,
        "ecart_valeur": valeur,
        "justification": x.justification,
        "compte_par": x.compte_par,
    }

def campagne_json(c):
    lignes = [ligne_json(x) for x in c.lignes]
    return {
        "id": c.id, "reference": c.reference, "libelle": c.libelle, "statut": c.statut,
        "date_creation": c.date_creation, "date_comptage": c.date_comptage,
        "date_validation": c.date_validation, "cree_par": c.cree_par, "valide_par": c.valide_par,
        "commentaire": c.commentaire, "lignes": lignes,
        "nb_lignes": len(lignes),
        "nb_comptees": sum(x["quantite_comptee"] is not None for x in lignes),
        "ecart_valeur_total": sum((x["ecart_valeur"] or Decimal("0")) for x in lignes),
    }

@router.get("")
def liste(db: Session = Depends(get_db), _: Utilisateur = Depends(utilisateur_courant)):
    rows = db.scalars(select(CampagneInventaireAvance).order_by(CampagneInventaireAvance.date_creation.desc())).unique().all()
    return [campagne_json(x) for x in rows]

@router.post("")
def creer(p: CampagneCreate, db: Session = Depends(get_db), u: Utilisateur = Depends(utilisateur_courant)):
    numero = (db.scalar(select(func.max(CampagneInventaireAvance.id))) or 0) + 1
    c = CampagneInventaireAvance(reference=f"INV-{numero:06d}", libelle=p.libelle.strip(),
        statut="EN_COMPTAGE", date_comptage=p.date_comptage or date.today(),
        commentaire=p.commentaire, cree_par=u.nom_complet)
    db.add(c); db.flush()

    q = select(Stock).where(Stock.quantite >= 0)
    if p.emplacement_id:
        q = q.where(Stock.emplacement_id == p.emplacement_id)
    stocks = db.scalars(q).all()
    for s in stocks:
        art = db.get(Article, s.article_id)
        if p.famille_id and getattr(art, "famille_id", None) != p.famille_id:
            continue
        prix = Decimal(str(getattr(art, "prix_achat", 0) or getattr(art, "prix_unitaire", 0) or 0))
        db.add(LigneInventaireAvance(campagne_id=c.id, article_id=s.article_id, emplacement_id=s.emplacement_id,
            quantite_theorique=s.quantite, prix_unitaire=prix))
    db.commit(); db.refresh(c)
    return campagne_json(c)

@router.patch("/lignes/{ligne_id}")
def compter(ligne_id: int, p: Comptage, db: Session = Depends(get_db), u: Utilisateur = Depends(utilisateur_courant)):
    x = db.get(LigneInventaireAvance, ligne_id)
    if not x: raise HTTPException(404, "Ligne introuvable.")
    if x.campagne.statut != "EN_COMPTAGE": raise HTTPException(409, "Cette campagne n'est plus en comptage.")
    ecart = p.quantite_comptee - x.quantite_theorique
    if ecart != 0 and not (p.justification or "").strip():
        raise HTTPException(422, "Une justification est obligatoire lorsqu'un ecart est constate.")
    x.quantite_comptee = p.quantite_comptee
    x.justification = (p.justification or "").strip() or None
    x.compte_par = u.nom_complet
    x.date_comptage = datetime.now(timezone.utc)
    db.commit(); db.refresh(x)
    return ligne_json(x)

@router.post("/{campagne_id}/valider")
def valider(campagne_id: int, db: Session = Depends(get_db), u: Utilisateur = Depends(utilisateur_courant)):
    c = db.scalar(select(CampagneInventaireAvance).where(CampagneInventaireAvance.id == campagne_id).with_for_update())
    if not c: raise HTTPException(404, "Campagne introuvable.")
    if c.statut != "EN_COMPTAGE": raise HTTPException(409, "Campagne deja validee ou cloturee.")
    if any(x.quantite_comptee is None for x in c.lignes):
        raise HTTPException(422, "Toutes les lignes doivent etre comptees avant validation.")

    for x in c.lignes:
        ecart = x.quantite_comptee - x.quantite_theorique
        if ecart == 0: continue
        stock = db.scalar(select(Stock).where(
            Stock.article_id == x.article_id, Stock.emplacement_id == x.emplacement_id
        ).with_for_update())
        if not stock: raise HTTPException(409, "Stock introuvable lors de la regularisation.")
        stock.quantite = x.quantite_comptee
        db.add(MouvementStock(
            article_id=x.article_id, emplacement_id=x.emplacement_id,
            type_mouvement="AJUSTEMENT_INVENTAIRE", quantite=ecart,
            commentaire=f"{c.reference} - {x.justification}",
            utilisateur=u.nom_complet,
        ))
    c.statut = "VALIDEE"
    c.date_validation = datetime.now(timezone.utc)
    c.valide_par = u.nom_complet
    db.commit(); db.refresh(c)
    return campagne_json(c)
