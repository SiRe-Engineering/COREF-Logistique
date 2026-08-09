import base64
import binascii
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.achats import CommandeAchat, Fournisseur
from app.models.article import Article
from app.models.document_fournisseur import DocumentFournisseur
from app.models.lot_beton import LotBeton
from app.models.utilisateur import Utilisateur
from app.schemas.document_fournisseur import (
    DocumentCreate,
    DocumentRead,
    StatutDocumentaireLotRead,
)


router = APIRouter(
    prefix="/api/documents-fournisseurs",
    tags=["Documents fournisseurs"],
)

TAILLE_MAX = 15 * 1024 * 1024
MIME_AUTORISES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/webp",
}


def _decoder(contenu_base64: str) -> bytes:
    valeur = contenu_base64
    if "," in valeur and valeur.lstrip().startswith("data:"):
        valeur = valeur.split(",", 1)[1]
    try:
        contenu = base64.b64decode(valeur, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise HTTPException(
            status_code=422,
            detail="Le contenu du fichier est invalide.",
        ) from exc
    if not contenu:
        raise HTTPException(status_code=422, detail="Le fichier est vide.")
    if len(contenu) > TAILLE_MAX:
        raise HTTPException(
            status_code=413,
            detail="Le fichier dépasse la limite de 15 Mo.",
        )
    return contenu


def _verifier_cibles(db: Session, payload: DocumentCreate) -> None:
    if payload.lot_beton_id and db.get(LotBeton, payload.lot_beton_id) is None:
        raise HTTPException(status_code=404, detail="Lot béton introuvable.")
    if payload.fournisseur_id and db.get(Fournisseur, payload.fournisseur_id) is None:
        raise HTTPException(status_code=404, detail="Fournisseur introuvable.")
    if payload.commande_achat_id and db.get(CommandeAchat, payload.commande_achat_id) is None:
        raise HTTPException(status_code=404, detail="Commande introuvable.")
    if payload.article_id and db.get(Article, payload.article_id) is None:
        raise HTTPException(status_code=404, detail="Article introuvable.")


@router.get("", response_model=list[DocumentRead])
def lister(
    lot_beton_id: int | None = None,
    fournisseur_id: int | None = None,
    commande_achat_id: int | None = None,
    article_id: int | None = None,
    type_document: str | None = Query(default=None, max_length=40),
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    q = select(DocumentFournisseur).order_by(
        DocumentFournisseur.date_depot.desc()
    )
    if lot_beton_id is not None:
        q = q.where(DocumentFournisseur.lot_beton_id == lot_beton_id)
    if fournisseur_id is not None:
        q = q.where(DocumentFournisseur.fournisseur_id == fournisseur_id)
    if commande_achat_id is not None:
        q = q.where(
            DocumentFournisseur.commande_achat_id == commande_achat_id
        )
    if article_id is not None:
        q = q.where(DocumentFournisseur.article_id == article_id)
    if type_document:
        q = q.where(DocumentFournisseur.type_document == type_document)
    return list(db.scalars(q).all())


@router.post(
    "",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def deposer(
    payload: DocumentCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
):
    _verifier_cibles(db, payload)
    if payload.type_mime not in MIME_AUTORISES:
        raise HTTPException(
            status_code=422,
            detail="Formats autorisés : PDF, PNG, JPG/JPEG, WEBP.",
        )

    contenu = _decoder(payload.contenu_base64)
    doc = DocumentFournisseur(
        type_document=payload.type_document,
        nom_fichier=payload.nom_fichier,
        type_mime=payload.type_mime,
        taille_octets=len(contenu),
        contenu=contenu,
        lot_beton_id=payload.lot_beton_id,
        fournisseur_id=payload.fournisseur_id,
        commande_achat_id=payload.commande_achat_id,
        article_id=payload.article_id,
        reference_document=payload.reference_document,
        date_document=payload.date_document,
        date_expiration=payload.date_expiration,
        commentaire=payload.commentaire,
        depose_par=utilisateur.nom_complet,
    )
    db.add(doc)

    if payload.lot_beton_id:
        lot = db.get(LotBeton, payload.lot_beton_id)
        if payload.type_document == "CERTIFICAT":
            lot.certificat_reference = (
                payload.reference_document or payload.nom_fichier
            )
        elif payload.type_document == "FDS":
            lot.fds_reference = (
                payload.reference_document or payload.nom_fichier
            )

    db.commit()
    db.refresh(doc)
    return doc


@router.get("/{document_id}/fichier")
def telecharger(
    document_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    doc = db.get(DocumentFournisseur, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    nom = doc.nom_fichier.replace('"', "")
    return Response(
        content=doc.contenu,
        media_type=doc.type_mime,
        headers={
            "Content-Disposition": f'inline; filename="{nom}"',
            "Cache-Control": "private, max-age=3600",
        },
    )


@router.delete("/{document_id}", status_code=204)
def supprimer(
    document_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    doc = db.get(DocumentFournisseur, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    lot_id = doc.lot_beton_id
    type_document = doc.type_document
    db.delete(doc)
    db.flush()

    if lot_id and type_document in {"CERTIFICAT", "FDS"}:
        lot = db.get(LotBeton, lot_id)
        restant = db.scalar(
            select(DocumentFournisseur.id)
            .where(
                DocumentFournisseur.lot_beton_id == lot_id,
                DocumentFournisseur.type_document == type_document,
            )
            .limit(1)
        )
        if restant is None and lot is not None:
            if type_document == "CERTIFICAT":
                lot.certificat_reference = None
            else:
                lot.fds_reference = None

    db.commit()


@router.get(
    "/lots/statuts",
    response_model=list[StatutDocumentaireLotRead],
)
def statuts_lots(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    lots = list(
        db.scalars(
            select(LotBeton)
            .where(
                LotBeton.actif.is_(True),
                LotBeton.supprime.is_(False),
            )
            .order_by(LotBeton.reference_interne)
        ).all()
    )
    docs = list(
        db.scalars(
            select(DocumentFournisseur)
            .where(DocumentFournisseur.lot_beton_id.is_not(None))
            .order_by(DocumentFournisseur.date_depot.desc())
        ).all()
    )
    par_lot: dict[int, list[DocumentFournisseur]] = {}
    for doc in docs:
        par_lot.setdefault(doc.lot_beton_id, []).append(doc)

    resultat = []
    aujourd_hui = date.today()
    for lot in lots:
        lot_docs = par_lot.get(lot.id, [])
        certificat = any(
            d.type_document == "CERTIFICAT" for d in lot_docs
        )
        fds_docs = [
            d for d in lot_docs if d.type_document == "FDS"
        ]
        fds = bool(fds_docs)
        expire = any(
            d.date_expiration is not None
            and d.date_expiration < aujourd_hui
            for d in fds_docs
        )
        if expire:
            statut = "EXPIRE"
        elif fds:
            statut = "COMPLET"
        else:
            statut = "INCOMPLET"

        resultat.append(
            StatutDocumentaireLotRead(
                lot_id=lot.id,
                reference_interne=lot.reference_interne,
                article_reference=lot.article.reference,
                article_designation=lot.article.designation,
                certificat_present=certificat,
                fds_presente=fds,
                document_expire=expire,
                statut=statut,
                documents=lot_docs,
            )
        )
    return resultat
