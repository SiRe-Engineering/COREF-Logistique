from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        index=True,
        server_default=text(
            "'ART-' || lpad(nextval('article_reference_seq')::text, 6, '0')"
        ),
    )
    designation: Mapped[str] = mapped_column(String(255), index=True)

    famille: Mapped[str | None] = mapped_column(String(120), nullable=True)
    sous_famille: Mapped[str | None] = mapped_column(String(120), nullable=True)

    famille_id: Mapped[int | None] = mapped_column(
        ForeignKey("familles.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )
    sous_famille_id: Mapped[int | None] = mapped_column(
        ForeignKey("sous_familles.id", ondelete="RESTRICT"),
        index=True,
        nullable=True,
    )

    unite: Mapped[str] = mapped_column(String(30), default="unité")
    stock_minimum: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    stock_maximum: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    seuil_alerte: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    famille_relation = relationship(
        "Famille",
        foreign_keys=[famille_id],
        lazy="joined",
    )
    sous_famille_relation = relationship(
        "SousFamille",
        foreign_keys=[sous_famille_id],
        lazy="joined",
    )
