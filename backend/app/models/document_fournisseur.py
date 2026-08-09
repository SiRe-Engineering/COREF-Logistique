from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DocumentFournisseur(Base):
    __tablename__ = "documents_fournisseurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    type_document: Mapped[str] = mapped_column(String(40), index=True)
    nom_fichier: Mapped[str] = mapped_column(String(255))
    type_mime: Mapped[str] = mapped_column(String(120))
    taille_octets: Mapped[int] = mapped_column(Integer)
    contenu: Mapped[bytes] = mapped_column(LargeBinary)

    lot_beton_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots_beton.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    fournisseur_id: Mapped[int | None] = mapped_column(
        ForeignKey("fournisseurs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    commande_achat_id: Mapped[int | None] = mapped_column(
        ForeignKey("commandes_achat.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    article_id: Mapped[int | None] = mapped_column(
        ForeignKey("articles.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    reference_document: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    date_document: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_expiration: Mapped[date | None] = mapped_column(Date, nullable=True)
    commentaire: Mapped[str | None] = mapped_column(Text, nullable=True)
    depose_par: Mapped[str | None] = mapped_column(String(150), nullable=True)
    date_depot: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    lot_beton = relationship("LotBeton", lazy="joined")
    fournisseur = relationship("Fournisseur", lazy="joined")
    commande_achat = relationship("CommandeAchat", lazy="joined")
    article = relationship("Article", lazy="joined")
