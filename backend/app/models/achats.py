from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Fournisseur(Base):
    __tablename__ = "fournisseurs"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(30), unique=True)
    raison_sociale: Mapped[str] = mapped_column(String(180), index=True)
    contact: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str | None] = mapped_column(String(180), nullable=True)
    telephone: Mapped[str | None] = mapped_column(String(60), nullable=True)
    adresse: Mapped[str | None] = mapped_column(Text, nullable=True)
    conditions_paiement: Mapped[str | None] = mapped_column(String(120), nullable=True)
    delai_habituel_jours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ArticleFournisseur(Base):
    __tablename__ = "articles_fournisseurs"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"))
    fournisseur_id: Mapped[int] = mapped_column(ForeignKey("fournisseurs.id", ondelete="CASCADE"))
    reference_fournisseur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    prix_unitaire_ht: Mapped[Decimal | None] = mapped_column(Numeric(14,4), nullable=True)
    delai_jours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minimum_commande: Mapped[Decimal | None] = mapped_column(Numeric(14,3), nullable=True)
    fournisseur_prefere: Mapped[bool] = mapped_column(Boolean, default=False)
    date_maj_prix: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    article = relationship("Article", lazy="joined")
    fournisseur = relationship("Fournisseur", lazy="joined")


class CommandeAchat(Base):
    __tablename__ = "commandes_achat"
    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(30), unique=True,
        server_default=text("'CMD-' || lpad(nextval('commande_achat_reference_seq')::text, 6, '0')")
    )
    fournisseur_id: Mapped[int] = mapped_column(ForeignKey("fournisseurs.id", ondelete="RESTRICT"), index=True)
    statut: Mapped[str] = mapped_column(String(35), default="BROUILLON", index=True)
    reference_fournisseur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    date_commande: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    date_livraison_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    cree_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    fournisseur = relationship("Fournisseur", lazy="joined")
    lignes = relationship("LigneCommandeAchat", cascade="all, delete-orphan", lazy="selectin", order_by="LigneCommandeAchat.id")


class LigneCommandeAchat(Base):
    __tablename__ = "lignes_commandes_achat"
    id: Mapped[int] = mapped_column(primary_key=True)
    commande_id: Mapped[int] = mapped_column(ForeignKey("commandes_achat.id", ondelete="CASCADE"), index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="RESTRICT"))
    besoin_reapprovisionnement_id: Mapped[int | None] = mapped_column(ForeignKey("besoins_reapprovisionnement.id", ondelete="SET NULL"), nullable=True)
    reference_fournisseur: Mapped[str | None] = mapped_column(String(120), nullable=True)
    quantite_commandee: Mapped[Decimal] = mapped_column(Numeric(14,3))
    quantite_recue: Mapped[Decimal] = mapped_column(Numeric(14,3), default=0)
    prix_unitaire_ht: Mapped[Decimal] = mapped_column(Numeric(14,4))
    article = relationship("Article", lazy="joined")
    besoin = relationship("BesoinReapprovisionnement", lazy="joined")



class HistoriquePrixFournisseur(Base):
    __tablename__ = "historique_prix_fournisseurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_fournisseur_id: Mapped[int] = mapped_column(
        ForeignKey("articles_fournisseurs.id", ondelete="CASCADE"),
        index=True,
    )
    prix_unitaire_ht: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    date_effet: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    modifie_par: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)

    article_fournisseur = relationship(
        "ArticleFournisseur",
        lazy="joined",
    )
