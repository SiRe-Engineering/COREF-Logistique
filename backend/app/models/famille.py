from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Famille(Base):
    __tablename__ = "familles"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True)
    nom: Mapped[str] = mapped_column(String(120), unique=True)
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    sous_familles: Mapped[list["SousFamille"]] = relationship(
        back_populates="famille",
        order_by="SousFamille.nom",
    )


class SousFamille(Base):
    __tablename__ = "sous_familles"
    __table_args__ = (
        UniqueConstraint("famille_id", "code", name="uq_sous_familles_famille_code"),
        UniqueConstraint("famille_id", "nom", name="uq_sous_familles_famille_nom"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    famille_id: Mapped[int] = mapped_column(
        ForeignKey("familles.id", ondelete="RESTRICT"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(10))
    nom: Mapped[str] = mapped_column(String(120))
    actif: Mapped[bool] = mapped_column(Boolean, default=True)
    date_creation: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    famille: Mapped[Famille] = relationship(back_populates="sous_familles")
