from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stock(Base):
    __tablename__ = "stocks"
    __table_args__ = (
        UniqueConstraint(
            "article_id",
            "emplacement_id",
            name="uq_stocks_article_emplacement",
        ),
        CheckConstraint(
            "quantite_physique >= 0",
            name="ck_stocks_quantite_physique_positive",
        ),
        CheckConstraint(
            "quantite_reservee >= 0",
            name="ck_stocks_quantite_reservee_positive",
        ),
        CheckConstraint(
            "quantite_reservee <= quantite_physique",
            name="ck_stocks_reservee_inferieure_physique",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id", ondelete="RESTRICT"),
        index=True,
    )
    emplacement_id: Mapped[int] = mapped_column(
        ForeignKey("emplacements.id", ondelete="RESTRICT"),
        index=True,
    )
    quantite_physique: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    quantite_reservee: Mapped[Decimal] = mapped_column(
        Numeric(14, 3),
        default=0,
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    article = relationship("Article", lazy="joined")
    emplacement = relationship("Emplacement", lazy="joined")

    @property
    def quantite_disponible(self) -> Decimal:
        return self.quantite_physique - self.quantite_reservee


# Propriétés de valorisation : le CUMP est porté par l'article.
def _valeur_stock(quantite: Decimal, cout: Decimal | None) -> Decimal:
    return quantite * (cout or Decimal("0"))


Stock.valeur_physique = property(
    lambda self: _valeur_stock(
        self.quantite_physique,
        self.article.cout_unitaire_moyen,
    )
)
Stock.valeur_reservee = property(
    lambda self: _valeur_stock(
        self.quantite_reservee,
        self.article.cout_unitaire_moyen,
    )
)
Stock.valeur_disponible = property(
    lambda self: _valeur_stock(
        self.quantite_disponible,
        self.article.cout_unitaire_moyen,
    )
)
