from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.utilisateur import Utilisateur

router = APIRouter(prefix="/api/alertes-logistiques", tags=["Alertes logistiques"])


def _get_model(name):
    """Resolve an already-registered SQLAlchemy model without duplicating mappings."""
    from app.db.base import Base
    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if cls.__name__ == name:
            return cls
    return None


def _value(obj, *names, default=None):
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def _as_date(v):
    if isinstance(v, datetime):
        return v.date()
    return v


def _alert(key, niveau, categorie, titre, detail, href, objet_id=None, echeance=None):
    return {
        "key": key,
        "niveau": niveau,
        "categorie": categorie,
        "titre": titre,
        "detail": detail,
        "href": href,
        "objet_id": objet_id,
        "echeance": echeance,
    }


@router.get("")
def liste_alertes(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    today = date.today()
    alerts = []

    # 1. Stocks au mini / sous mini.
    Stock = _get_model("Stock")
    Article = _get_model("Article")
    if Stock and Article:
        for s in db.scalars(select(Stock)).all():
            art = db.get(Article, _value(s, "article_id"))
            if not art:
                continue
            qte = Decimal(str(_value(s, "quantite", "quantite_disponible", default=0) or 0))
            mini = _value(art, "stock_minimum", "stock_mini", "seuil_alerte")
            if mini is None:
                continue
            mini = Decimal(str(mini))
            if qte <= mini:
                niveau = "CRITIQUE" if qte < mini else "ATTENTION"
                alerts.append(_alert(
                    f"stock:{art.id}:{_value(s,'emplacement_id',default=0)}",
                    niveau, "STOCK",
                    f"Stock {'sous' if qte < mini else 'au'} minimum",
                    f"{_value(art,'reference',default='Article')} — {_value(art,'designation',default='')} : {qte:g} / mini {mini:g}",
                    "/approvisionnements",
                    art.id,
                ))

    # 2. Commandes fournisseurs en retard.
    Commande = _get_model("CommandeFournisseur")
    if Commande:
        for c in db.scalars(select(Commande)).all():
            statut = str(_value(c, "statut", default="")).upper()
            if statut in {"LIVREE", "LIVRE", "ANNULEE", "ANNULE", "CLOTUREE", "CLOTURE"}:
                continue
            d = _as_date(_value(c, "date_livraison_prevue", "date_prevue", "date_attendue"))
            if d and d < today:
                alerts.append(_alert(
                    f"commande:{c.id}", "CRITIQUE", "APPRO",
                    "Commande fournisseur en retard",
                    f"{_value(c,'reference','numero',default='Commande')} — prévue le {d.strftime('%d/%m/%Y')}",
                    "/approvisionnements", c.id, d,
                ))

    # 3. Documents matériel expirés / à échéance.
    Doc = _get_model("DocumentMateriel")
    if Doc:
        for d in db.scalars(select(Doc)).all():
            exp = _as_date(_value(d, "date_expiration"))
            if not exp:
                continue
            materiel = _value(d, "materiel")
            ident = _value(materiel, "numero_inventaire", default="Matériel") if materiel else "Matériel"
            if exp < today:
                alerts.append(_alert(
                    f"docmat:{d.id}", "CRITIQUE", "MATERIEL",
                    "Document matériel expiré",
                    f"{ident} — {_value(d,'nom_fichier',default='document')} expiré le {exp.strftime('%d/%m/%Y')}",
                    "/documents-materiel", d.id, exp,
                ))
            elif exp <= today + timedelta(days=30):
                alerts.append(_alert(
                    f"docmat:{d.id}", "ATTENTION", "MATERIEL",
                    "Document matériel à renouveler",
                    f"{ident} — échéance le {exp.strftime('%d/%m/%Y')}",
                    "/documents-materiel", d.id, exp,
                ))

    # 4. Maintenances / contrôles matériel.
    Maintenance = _get_model("MaintenanceMateriel")
    if Maintenance:
        for m in db.scalars(select(Maintenance)).all():
            d = _as_date(_value(m, "date_prochaine", "date_echeance", "date_prevue"))
            statut = str(_value(m, "statut", default="")).upper()
            if not d or statut in {"REALISEE", "TERMINEE", "ANNULEE"}:
                continue
            mat = _value(m, "materiel")
            ident = _value(mat, "numero_inventaire", default="Matériel") if mat else "Matériel"
            if d < today:
                alerts.append(_alert(
                    f"maintenance:{m.id}", "CRITIQUE", "MATERIEL",
                    "Maintenance matériel en retard",
                    f"{ident} — échéance dépassée depuis le {d.strftime('%d/%m/%Y')}",
                    "/maintenance-materiel", m.id, d,
                ))
            elif d <= today + timedelta(days=30):
                alerts.append(_alert(
                    f"maintenance:{m.id}", "ATTENTION", "MATERIEL",
                    "Maintenance matériel à prévoir",
                    f"{ident} — prévue le {d.strftime('%d/%m/%Y')}",
                    "/maintenance-materiel", m.id, d,
                ))

    # 5. Préparations en retard.
    Preparation = _get_model("Preparation")
    if Preparation:
        for p in db.scalars(select(Preparation)).all():
            statut = str(_value(p, "statut", default="")).upper()
            if statut in {"TERMINEE", "LIVREE", "ANNULEE", "CLOTUREE"}:
                continue
            d = _as_date(_value(p, "date_fin_prevue", "fin_prevue", "date_prevue"))
            if d and d < today:
                alerts.append(_alert(
                    f"prep:{p.id}", "CRITIQUE", "PREPARATION",
                    "Préparation en retard",
                    f"{_value(p,'code','reference',default='Préparation')} — échéance {d.strftime('%d/%m/%Y')}",
                    "/preparations", p.id, d,
                ))

    # 6. Inventaires avancés non finalisés.
    Campagne = _get_model("CampagneInventaireAvance")
    if Campagne:
        for c in db.scalars(select(Campagne)).unique().all():
            if str(_value(c, "statut", default="")).upper() == "EN_COMPTAGE":
                total = len(_value(c, "lignes", default=[]) or [])
                done = sum(_value(x, "quantite_comptee") is not None for x in (_value(c, "lignes", default=[]) or []))
                alerts.append(_alert(
                    f"inventaire:{c.id}", "INFO", "INVENTAIRE",
                    "Inventaire en cours",
                    f"{_value(c,'reference',default='Inventaire')} — {done}/{total} lignes comptées",
                    "/inventaire/avance", c.id,
                ))

    ordre = {"CRITIQUE": 0, "ATTENTION": 1, "INFO": 2}
    alerts.sort(key=lambda x: (ordre.get(x["niveau"], 9), x["echeance"] or date.max))
    return {
        "total": len(alerts),
        "critiques": sum(x["niveau"] == "CRITIQUE" for x in alerts),
        "attention": sum(x["niveau"] == "ATTENTION" for x in alerts),
        "info": sum(x["niveau"] == "INFO" for x in alerts),
        "alertes": alerts,
        "genere_le": datetime.now(timezone.utc),
    }
