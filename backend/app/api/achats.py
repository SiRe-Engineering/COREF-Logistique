from datetime import datetime, timezone
import base64
import binascii
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies import utilisateur_courant
from app.models.achats import (
    ArticleFournisseur,
    CommandeAchat,
    Fournisseur,
    HistoriquePrixFournisseur,
    LigneCommandeAchat,
)
from app.models.article import Article
from app.models.document_fournisseur import DocumentFournisseur
from app.models.famille import Famille
from app.models.lot_beton import LotBeton
from app.models.reception_achat import ReceptionAchat
from app.models.reapprovisionnement import BesoinReapprovisionnement
from app.models.utilisateur import Utilisateur
from app.schemas.achats import (
    ArticleFournisseurCreate,
    ArticleFournisseurRead,
    ArticleFournisseurUpdate,
    CommandeCreate,
    CommandeRead,
    CommandeUpdate,
    FournisseurCreate,
    FournisseurRead,
    FournisseurUpdate,
    HistoriquePrixFournisseurRead,
    ReceptionLigneCreate,
    ReceptionLigneResult,
)
from app.schemas.mouvement import MouvementCreate
from app.services.mouvements import executer_mouvement


router = APIRouter(prefix="/api/achats", tags=["Achats fournisseurs"])


def _commande(db: Session, commande_id: int) -> CommandeAchat:
    commande = db.scalar(
        select(CommandeAchat)
        .options(selectinload(CommandeAchat.lignes))
        .where(CommandeAchat.id == commande_id)
    )
    if commande is None:
        raise HTTPException(status_code=404, detail="Commande introuvable.")
    return commande


def _lien_article_fournisseur(
    db: Session,
    lien_id: int,
) -> ArticleFournisseur:
    lien = db.get(ArticleFournisseur, lien_id)
    if lien is None:
        raise HTTPException(
            status_code=404,
            detail="Association article / fournisseur introuvable.",
        )
    return lien


def _enregistrer_prix(
    db: Session,
    lien: ArticleFournisseur,
    prix: Decimal,
    utilisateur: Utilisateur,
    commentaire: str | None = None,
) -> None:
    db.add(
        HistoriquePrixFournisseur(
            article_fournisseur_id=lien.id,
            prix_unitaire_ht=prix,
            modifie_par=utilisateur.nom_complet,
            commentaire=commentaire,
        )
    )
    lien.date_maj_prix = datetime.now(timezone.utc)


def _rendre_prefere_unique(
    db: Session,
    article_id: int,
    lien_a_conserver: int | None = None,
) -> None:
    liens = db.scalars(
        select(ArticleFournisseur).where(
            ArticleFournisseur.article_id == article_id,
        )
    ).all()
    for lien in liens:
        if lien.id != lien_a_conserver:
            lien.fournisseur_prefere = False


@router.get("/fournisseurs", response_model=list[FournisseurRead])
def fournisseurs(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    return list(
        db.scalars(
            select(Fournisseur).order_by(Fournisseur.raison_sociale)
        ).all()
    )


@router.post(
    "/fournisseurs",
    response_model=FournisseurRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_fournisseur(
    payload: FournisseurCreate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    donnees = payload.model_dump()
    donnees["code"] = payload.code.strip().upper()
    fournisseur = Fournisseur(**donnees)
    db.add(fournisseur)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code fournisseur existe déjà.",
        )
    db.refresh(fournisseur)
    return fournisseur


@router.patch(
    "/fournisseurs/{fournisseur_id}",
    response_model=FournisseurRead,
)
def modifier_fournisseur(
    fournisseur_id: int,
    payload: FournisseurUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    fournisseur = db.get(Fournisseur, fournisseur_id)
    if fournisseur is None:
        raise HTTPException(status_code=404, detail="Fournisseur introuvable.")

    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        if champ == "code" and valeur:
            valeur = valeur.strip().upper()
        setattr(fournisseur, champ, valeur)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce code fournisseur existe déjà.",
        )
    db.refresh(fournisseur)
    return fournisseur


@router.get(
    "/articles-fournisseurs",
    response_model=list[ArticleFournisseurRead],
)
def liens(
    article_id: int | None = None,
    fournisseur_id: int | None = None,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    requete = select(ArticleFournisseur).order_by(
        ArticleFournisseur.article_id,
        ArticleFournisseur.fournisseur_prefere.desc(),
    )
    if article_id is not None:
        requete = requete.where(
            ArticleFournisseur.article_id == article_id
        )
    if fournisseur_id is not None:
        requete = requete.where(
            ArticleFournisseur.fournisseur_id == fournisseur_id
        )
    return list(db.scalars(requete).unique().all())


@router.post(
    "/articles-fournisseurs",
    response_model=ArticleFournisseurRead,
    status_code=status.HTTP_201_CREATED,
)
def lier(
    payload: ArticleFournisseurCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
):
    if (
        db.get(Article, payload.article_id) is None
        or db.get(Fournisseur, payload.fournisseur_id) is None
    ):
        raise HTTPException(
            status_code=404,
            detail="Article ou fournisseur introuvable.",
        )

    lien = ArticleFournisseur(
        **payload.model_dump(),
        date_maj_prix=(
            datetime.now(timezone.utc)
            if payload.prix_unitaire_ht is not None
            else None
        ),
    )
    db.add(lien)

    try:
        db.flush()
        if payload.fournisseur_prefere:
            _rendre_prefere_unique(
                db,
                payload.article_id,
                lien.id,
            )
        if payload.prix_unitaire_ht is not None:
            _enregistrer_prix(
                db,
                lien,
                payload.prix_unitaire_ht,
                utilisateur,
                "Tarif initial",
            )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Ce fournisseur est déjà associé à cet article.",
        )

    db.refresh(lien)
    return lien


@router.patch(
    "/articles-fournisseurs/{lien_id}",
    response_model=ArticleFournisseurRead,
)
def modifier_lien(
    lien_id: int,
    payload: ArticleFournisseurUpdate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
):
    lien = _lien_article_fournisseur(db, lien_id)
    donnees = payload.model_dump(exclude_unset=True)
    commentaire_prix = donnees.pop("commentaire_prix", None)

    prix_fourni = "prix_unitaire_ht" in donnees
    nouveau_prix = donnees.get("prix_unitaire_ht")
    ancien_prix = lien.prix_unitaire_ht

    if donnees.get("fournisseur_prefere") is True:
        _rendre_prefere_unique(db, lien.article_id, lien.id)

    for champ, valeur in donnees.items():
        setattr(lien, champ, valeur)

    if (
        prix_fourni
        and nouveau_prix is not None
        and nouveau_prix != ancien_prix
    ):
        _enregistrer_prix(
            db,
            lien,
            nouveau_prix,
            utilisateur,
            commentaire_prix,
        )

    db.commit()
    db.refresh(lien)
    return lien


@router.delete("/articles-fournisseurs/{lien_id}", status_code=204)
def supprimer_lien(
    lien_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    lien = _lien_article_fournisseur(db, lien_id)
    db.delete(lien)
    db.commit()


@router.get(
    "/articles-fournisseurs/{lien_id}/historique",
    response_model=list[HistoriquePrixFournisseurRead],
)
def historique_prix(
    lien_id: int,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    _lien_article_fournisseur(db, lien_id)
    return list(
        db.scalars(
            select(HistoriquePrixFournisseur)
            .where(
                HistoriquePrixFournisseur.article_fournisseur_id
                == lien_id
            )
            .order_by(HistoriquePrixFournisseur.date_effet.desc())
        ).all()
    )


@router.get("/commandes", response_model=list[CommandeRead])
def commandes(
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    return list(
        db.scalars(
            select(CommandeAchat)
            .options(selectinload(CommandeAchat.lignes))
            .order_by(CommandeAchat.date_creation.desc())
        ).unique().all()
    )


@router.post(
    "/commandes",
    response_model=CommandeRead,
    status_code=status.HTTP_201_CREATED,
)
def creer_commande(
    payload: CommandeCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
):
    fournisseur = db.get(Fournisseur, payload.fournisseur_id)
    if fournisseur is None or not fournisseur.actif:
        raise HTTPException(
            status_code=404,
            detail="Fournisseur introuvable ou inactif.",
        )

    commande = CommandeAchat(
        fournisseur_id=fournisseur.id,
        date_livraison_prevue=payload.date_livraison_prevue,
        commentaire=payload.commentaire,
        cree_par=utilisateur.nom_complet,
    )
    db.add(commande)
    db.flush()

    for ligne_payload in payload.lignes:
        article = db.get(Article, ligne_payload.article_id)
        if article is None or not article.actif:
            raise HTTPException(
                status_code=404,
                detail=f"Article {ligne_payload.article_id} introuvable.",
            )

        besoin = None
        if ligne_payload.besoin_reapprovisionnement_id:
            besoin = db.get(
                BesoinReapprovisionnement,
                ligne_payload.besoin_reapprovisionnement_id,
            )
            if besoin is None or besoin.article_id != article.id:
                raise HTTPException(
                    status_code=422,
                    detail="Besoin incohérent avec l'article.",
                )
            if besoin.statut in {"RECU", "ANNULE"}:
                raise HTTPException(
                    status_code=409,
                    detail=f"Le besoin {besoin.reference} est clôturé.",
                )

        tarif = db.scalar(
            select(ArticleFournisseur).where(
                ArticleFournisseur.article_id == article.id,
                ArticleFournisseur.fournisseur_id == fournisseur.id,
            )
        )

        prix = (
            tarif.prix_unitaire_ht
            if tarif is not None and tarif.prix_unitaire_ht is not None
            else ligne_payload.prix_unitaire_ht
        )
        ref_fournisseur = (
            tarif.reference_fournisseur
            if tarif is not None and tarif.reference_fournisseur
            else ligne_payload.reference_fournisseur
        )

        quantite = ligne_payload.quantite_commandee
        if (
            tarif is not None
            and tarif.minimum_commande is not None
            and quantite < tarif.minimum_commande
        ):
            quantite = tarif.minimum_commande

        ligne = LigneCommandeAchat(
            commande_id=commande.id,
            article_id=article.id,
            besoin_reapprovisionnement_id=(
                ligne_payload.besoin_reapprovisionnement_id
            ),
            reference_fournisseur=ref_fournisseur,
            quantite_commandee=quantite,
            prix_unitaire_ht=prix,
        )
        db.add(ligne)

        if besoin is not None:
            besoin.quantite_commandee = quantite
            besoin.prix_unitaire_prevu = prix
            besoin.fournisseur = fournisseur.raison_sociale
            besoin.reference_commande = commande.reference
            besoin.statut = "COMMANDE"
            besoin.date_commande = datetime.now(timezone.utc)

    db.commit()
    db.refresh(commande)
    return _commande(db, commande.id)


@router.patch("/commandes/{commande_id}", response_model=CommandeRead)
def modifier_commande(
    commande_id: int,
    payload: CommandeUpdate,
    db: Session = Depends(get_db),
    _: Utilisateur = Depends(utilisateur_courant),
):
    commande = _commande(db, commande_id)
    if commande.statut in {"RECUE", "ANNULEE"}:
        raise HTTPException(
            status_code=409,
            detail="Cette commande est clôturée.",
        )

    ancien = commande.statut
    for champ, valeur in payload.model_dump(exclude_unset=True).items():
        setattr(commande, champ, valeur)

    if commande.statut == "ENVOYEE" and ancien != "ENVOYEE":
        commande.date_commande = datetime.now(timezone.utc)

    db.commit()
    return _commande(db, commande_id)


@router.post(
    "/commandes/{commande_id}/lignes/{ligne_id}/reception",
    response_model=ReceptionLigneResult,
)
def reception(
    commande_id: int,
    ligne_id: int,
    payload: ReceptionLigneCreate,
    db: Session = Depends(get_db),
    utilisateur: Utilisateur = Depends(utilisateur_courant),
):
    commande = _commande(db, commande_id)
    if commande.statut in {"BROUILLON", "ANNULEE", "RECUE"}:
        raise HTTPException(
            status_code=409,
            detail="La commande n'est pas réceptionnable dans cet état.",
        )

    ligne = next(
        (item for item in commande.lignes if item.id == ligne_id),
        None,
    )
    if ligne is None:
        raise HTTPException(
            status_code=404,
            detail="Ligne de commande introuvable.",
        )

    restant = ligne.quantite_commandee - ligne.quantite_recue
    if payload.quantite > restant:
        raise HTTPException(
            status_code=422,
            detail=f"Réception supérieure au solde attendu ({restant}).",
        )

    prix = (
        payload.prix_unitaire_ht
        if payload.prix_unitaire_ht is not None
        else ligne.prix_unitaire_ht
    )

    article = db.get(Article, ligne.article_id)
    famille = (
        db.get(Famille, article.famille_id)
        if article is not None and article.famille_id
        else None
    )
    est_beton = famille is not None and famille.code == "BET"

    lot = None
    fds_presente = None
    avertissements = []

    if est_beton:
        if payload.lot_id is None:
            raise HTTPException(
                status_code=422,
                detail="Un lot béton est obligatoire pour cette réception.",
            )
        lot = db.get(LotBeton, payload.lot_id)
        if lot is None or lot.article_id != ligne.article_id:
            raise HTTPException(
                status_code=422,
                detail="Le lot béton sélectionné ne correspond pas à l'article.",
            )
        fds_presente = db.scalar(
            select(DocumentFournisseur.id)
            .where(
                DocumentFournisseur.lot_beton_id == lot.id,
                DocumentFournisseur.type_document == "FDS",
            )
            .limit(1)
        ) is not None
        if not fds_presente:
            avertissements.append(
                "Réception béton enregistrée sans FDS disponible pour le lot."
            )

    statut_qualite = "CONFORME"
    if payload.conformite_visuelle == "NON_CONFORME":
        statut_qualite = "NON_CONFORME"
    elif payload.conformite_visuelle == "RESERVE":
        statut_qualite = "SOUS_RESERVE"
    elif est_beton and not fds_presente:
        statut_qualite = "A_CONTROLER"

    if payload.bon_livraison_contenu_base64:
        if not payload.bon_livraison_nom_fichier or not payload.bon_livraison_type_mime:
            raise HTTPException(
                status_code=422,
                detail="Nom et type du fichier BL sont obligatoires.",
            )
        if payload.bon_livraison_type_mime not in {
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/webp",
        }:
            raise HTTPException(
                status_code=422,
                detail="Le BL doit être un PDF ou une image.",
            )
        try:
            contenu_bl = base64.b64decode(
                payload.bon_livraison_contenu_base64,
                validate=True,
            )
        except (ValueError, binascii.Error) as exc:
            raise HTTPException(
                status_code=422,
                detail="Le fichier BL est invalide.",
            ) from exc
        if len(contenu_bl) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail="Le BL dépasse 15 Mo.",
            )
        db.add(
            DocumentFournisseur(
                type_document="BON_LIVRAISON",
                nom_fichier=payload.bon_livraison_nom_fichier,
                type_mime=payload.bon_livraison_type_mime,
                taille_octets=len(contenu_bl),
                contenu=contenu_bl,
                lot_beton_id=payload.lot_id,
                fournisseur_id=commande.fournisseur_id,
                commande_achat_id=commande.id,
                article_id=ligne.article_id,
                reference_document=payload.bon_livraison_reference,
                commentaire=payload.commentaire_qualite,
                depose_par=utilisateur.nom_complet,
            )
        )

    executer_mouvement(
        db,
        MouvementCreate(
            type="ENTREE",
            article_id=ligne.article_id,
            lot_id=payload.lot_id,
            besoin_reapprovisionnement_id=(
                ligne.besoin_reapprovisionnement_id
            ),
            ligne_commande_achat_id=ligne.id,
            emplacement_destination_id=payload.emplacement_destination_id,
            quantite=payload.quantite,
            prix_unitaire_ht=prix,
            motif=f"Réception {commande.reference}",
            commentaire=payload.commentaire,
            operateur=utilisateur.nom_complet,
        ),
        valider_transaction=False,
    )

    reception_qualite = ReceptionAchat(
        commande_id=commande.id,
        ligne_commande_id=ligne.id,
        article_id=ligne.article_id,
        lot_beton_id=payload.lot_id,
        quantite=payload.quantite,
        bon_livraison_reference=payload.bon_livraison_reference,
        conformite_visuelle=payload.conformite_visuelle,
        reserve_commentaire=payload.reserve_commentaire,
        commentaire_qualite=payload.commentaire_qualite,
        fds_presente=fds_presente,
        statut_qualite=statut_qualite,
        receptionne_par=utilisateur.nom_complet,
    )
    db.add(reception_qualite)
    db.flush()

    maintenant = datetime.now(timezone.utc)

    if ligne.date_premiere_reception is None:
        ligne.date_premiere_reception = maintenant
    ligne.date_derniere_reception = maintenant

    if commande.date_premiere_reception is None:
        commande.date_premiere_reception = maintenant

    ligne.quantite_recue += payload.quantite

    if ligne.besoin:
        ligne.besoin.quantite_recue += payload.quantite
        if (
            ligne.besoin.quantite_recue
            >= ligne.besoin.quantite_commandee
        ):
            ligne.besoin.statut = "RECU"
            ligne.besoin.date_cloture = datetime.now(timezone.utc)

    total = sum(
        (item.quantite_commandee for item in commande.lignes),
        start=Decimal("0"),
    )
    recu = sum(
        (item.quantite_recue for item in commande.lignes),
        start=Decimal("0"),
    )
    if recu >= total:
        commande.statut = "RECUE"
        commande.date_reception_finale = maintenant
    else:
        commande.statut = "PARTIELLEMENT_RECUE"

    db.commit()
    commande_lue = _commande(db, commande.id)
    return ReceptionLigneResult(
        commande=commande_lue,
        reception_id=reception_qualite.id,
        statut_qualite=statut_qualite,
        avertissements=avertissements,
    )
